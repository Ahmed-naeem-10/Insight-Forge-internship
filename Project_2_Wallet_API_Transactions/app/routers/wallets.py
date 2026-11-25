import uuid
from decimal import Decimal
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from sqlalchemy.orm import Session
from app.core.config import settings, logger
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.limiter import limiter
from app.models.user import User
from app.models.wallet import Wallet
from app.models.transaction import Transaction
from app.schemas.wallet import WalletCreate, WalletOut, WalletBalanceOut
from app.schemas.transaction import (
    DepositRequest,
    WithdrawRequest,
    TransferRequest,
    DirectTransferRequest,
    TransactionOut,
    TransactionDetailResponse,
)

router = APIRouter(prefix="/wallets", tags=["Wallets & Transactions"])


@router.get(
    "/me",
    response_model=List[WalletOut],
    summary="List all wallets for the authenticated user",
    description="Fetches all wallets associated with the currently authenticated user (retrieved directly from the JWT).",
)
def get_user_wallets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[WalletOut]:
    wallets = db.query(Wallet).filter(Wallet.user_id == current_user.user_id).all()
    return wallets


@router.get(
    "/{wallet_id}/balance",
    response_model=WalletBalanceOut,
    summary="Get wallet balance",
    description="Retrieves the current balance of a specific wallet. Enforces strict authorization so users can only view their own wallets.",
)
def get_wallet_balance(
    wallet_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WalletBalanceOut:
    wallet = db.query(Wallet).filter(Wallet.wallet_id == wallet_id).first()
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Wallet with ID {wallet_id} was not found.",
        )

    # Security check: Ensure the requesting user owns this wallet
    if wallet.user_id != current_user.user_id:
        logger.warning(
            f"Unauthorized balance access attempt: User {current_user.user_id} attempted to view Wallet {wallet_id} owned by User {wallet.user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not have permission to view this wallet's balance.",
        )

    return wallet


@router.post(
    "",
    response_model=WalletOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create an additional wallet",
    description="Creates a new supplementary wallet (e.g., a Savings wallet or a wallet in another currency) for the authenticated user.",
)
def create_wallet(
    wallet_in: WalletCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WalletOut:
    new_wallet = Wallet(
        user_id=current_user.user_id,
        currency=wallet_in.currency.upper(),
        balance=Decimal("0.00"),
        wallet_type=wallet_in.wallet_type,
    )
    db.add(new_wallet)
    db.commit()
    db.refresh(new_wallet)
    logger.info(f"Wallet created: ID {new_wallet.wallet_id} for User {current_user.user_id} ({new_wallet.currency} {new_wallet.wallet_type})")
    return new_wallet


# ============================================================================
# STEP 13 — DEPOSIT & WITHDRAWAL
# ============================================================================

@router.post(
    "/{wallet_id}/deposit",
    response_model=TransactionDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Deposit funds into wallet",
    description="Adds funds to a wallet inside an atomic transaction and records a Deposit Transaction without sender_wallet_id.",
)
@limiter.limit("30/minute")
def deposit_funds(
    request: Request,
    wallet_id: int,
    deposit_in: DepositRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TransactionDetailResponse:
    # 1. Check ownership
    wallet = db.query(Wallet).filter(Wallet.wallet_id == wallet_id).first()
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Wallet {wallet_id} not found.",
        )
    if wallet.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not own this wallet.",
        )

    # 2. Check Idempotency (Step 15)
    idempotency_str = str(deposit_in.idempotency_key) if deposit_in.idempotency_key else str(uuid.uuid4())
    existing_txn = db.query(Transaction).filter(Transaction.idempotency_key == idempotency_str).first()
    if existing_txn:
        logger.info(f"Idempotent deposit request hit: key={idempotency_str}, returning existing transaction {existing_txn.transaction_id}")
        return TransactionDetailResponse(
            message="Deposit request already processed (idempotent cached result)",
            transaction=TransactionOut.model_validate(existing_txn),
            updated_balance=wallet.balance,
            is_cached=True,
        )

    # 3. Process Deposit inside DB transaction
    try:
        wallet.balance += deposit_in.amount
        txn = Transaction(
            transaction_id=str(uuid.uuid4()),
            idempotency_key=idempotency_str,
            sender_wallet_id=None,
            receiver_wallet_id=wallet.wallet_id,
            transaction_type="Deposit",
            amount=deposit_in.amount,
            status="Completed",
            created_at=datetime.utcnow(),
        )
        db.add(txn)
        db.commit()
        db.refresh(wallet)
        db.refresh(txn)

        logger.info(f"Deposit successful: Wallet {wallet.wallet_id} +{deposit_in.amount} {wallet.currency} (Txn: {txn.transaction_id})")
        return TransactionDetailResponse(
            message="Deposit processed successfully",
            transaction=TransactionOut.model_validate(txn),
            updated_balance=wallet.balance,
            is_cached=False,
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Deposit failed for Wallet {wallet_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error processing deposit.",
        )


@router.post(
    "/{wallet_id}/withdraw",
    response_model=TransactionDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Withdraw funds from wallet",
    description="Subtracts funds from a wallet balance (ensuring non-negative check) and logs a Withdrawal Transaction row.",
)
@limiter.limit("30/minute")
def withdraw_funds(
    request: Request,
    wallet_id: int,
    withdraw_in: WithdrawRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TransactionDetailResponse:
    # 1. Check ownership
    wallet = db.query(Wallet).filter(Wallet.wallet_id == wallet_id).first()
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Wallet {wallet_id} not found.",
        )
    if wallet.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not own this wallet.",
        )

    # 2. Check Idempotency
    idempotency_str = str(withdraw_in.idempotency_key) if withdraw_in.idempotency_key else str(uuid.uuid4())
    existing_txn = db.query(Transaction).filter(Transaction.idempotency_key == idempotency_str).first()
    if existing_txn:
        logger.info(f"Idempotent withdraw request hit: key={idempotency_str}, returning existing transaction {existing_txn.transaction_id}")
        return TransactionDetailResponse(
            message="Withdrawal request already processed (idempotent cached result)",
            transaction=TransactionOut.model_validate(existing_txn),
            updated_balance=wallet.balance,
            is_cached=True,
        )

    # 3. Check sufficient funds
    if wallet.balance < withdraw_in.amount:
        logger.warning(f"Withdrawal overdraw rejected: Wallet {wallet.wallet_id} balance={wallet.balance}, requested={withdraw_in.amount}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient balance. Available: {wallet.balance} {wallet.currency}, Requested: {withdraw_in.amount} {wallet.currency}.",
        )

    # 4. Process Withdrawal inside DB transaction
    try:
        wallet.balance -= withdraw_in.amount
        txn = Transaction(
            transaction_id=str(uuid.uuid4()),
            idempotency_key=idempotency_str,
            sender_wallet_id=wallet.wallet_id,
            receiver_wallet_id=None,
            transaction_type="Withdrawal",
            amount=withdraw_in.amount,
            status="Completed",
            created_at=datetime.utcnow(),
        )
        db.add(txn)
        db.commit()
        db.refresh(wallet)
        db.refresh(txn)

        logger.info(f"Withdrawal successful: Wallet {wallet.wallet_id} -{withdraw_in.amount} {wallet.currency} (Txn: {txn.transaction_id})")
        return TransactionDetailResponse(
            message="Withdrawal processed successfully",
            transaction=TransactionOut.model_validate(txn),
            updated_balance=wallet.balance,
            is_cached=False,
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Withdrawal failed for Wallet {wallet_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error processing withdrawal.",
        )


# ============================================================================
# STEPS 14 & 15 — ATOMIC TRANSFER LOGIC WITH IDEMPOTENCY & ROW LOCKING
# ============================================================================

def execute_atomic_transfer(
    db: Session,
    sender_wallet_id: int,
    receiver_wallet_id: int,
    amount: Decimal,
    idempotency_key: str,
    current_user: User,
) -> TransactionDetailResponse:
    """Executes atomic transfer with row locking, idempotency check, balance validation, and audit logging."""

    # Rule: Cannot transfer to self
    if sender_wallet_id == receiver_wallet_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot transfer funds to the same wallet.",
        )

    # Idempotency check before touching balances (Step 15)
    existing_txn = db.query(Transaction).filter(Transaction.idempotency_key == idempotency_key).first()
    if existing_txn:
        sender = db.query(Wallet).filter(Wallet.wallet_id == sender_wallet_id).first()
        logger.info(f"Idempotent transfer hit for key: {idempotency_key} -> returning cached transaction {existing_txn.transaction_id}")
        return TransactionDetailResponse(
            message="Transfer already completed (idempotent result returned)",
            transaction=TransactionOut.model_validate(existing_txn),
            updated_balance=sender.balance if sender else None,
            is_cached=True,
        )

    try:
        # Deadlock prevention: Lock wallets in ascending ID order
        ordered_ids = sorted([sender_wallet_id, receiver_wallet_id])
        locked_wallets = {}

        for wid in ordered_ids:
            query = db.query(Wallet).filter(Wallet.wallet_id == wid)
            # Row locking for PostgreSQL (SQLite serializes writes automatically)
            if not db.bind.name.startswith("sqlite"):
                query = query.with_for_update()
            w = query.first()
            if not w:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Wallet {wid} does not exist.",
                )
            locked_wallets[wid] = w

        sender = locked_wallets[sender_wallet_id]
        receiver = locked_wallets[receiver_wallet_id]

        # Ownership verification
        if sender.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden: You can only transfer funds from your own wallet.",
            )

        # Currency compatibility
        if sender.currency.upper() != receiver.currency.upper():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Currency mismatch: Sender is in {sender.currency}, receiver is in {receiver.currency}. Multi-currency conversion is not enabled.",
            )

        # Re-check balance inside lock
        if sender.balance < amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient balance. Available: {sender.balance} {sender.currency}, Requested transfer: {amount} {sender.currency}.",
            )

        # Atomic balance mutation
        sender.balance -= amount
        receiver.balance += amount

        # Record permanent transaction record
        txn = Transaction(
            transaction_id=str(uuid.uuid4()),
            idempotency_key=idempotency_key,
            sender_wallet_id=sender.wallet_id,
            receiver_wallet_id=receiver.wallet_id,
            transaction_type="Transfer",
            amount=amount,
            status="Completed",
            created_at=datetime.utcnow(),
        )
        db.add(txn)
        db.commit()
        db.refresh(sender)
        db.refresh(txn)

        logger.info(
            f"Atomic Transfer Completed: Wallet {sender_wallet_id} -> Wallet {receiver_wallet_id}, Amount: {amount} {sender.currency}, Txn ID: {txn.transaction_id}"
        )

        return TransactionDetailResponse(
            message="Transfer completed successfully",
            transaction=TransactionOut.model_validate(txn),
            updated_balance=sender.balance,
            is_cached=False,
        )

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Atomic transfer failed unexpectedly: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error occurred during transfer. Transaction rolled back.",
        )


@router.post(
    "/{wallet_id}/transfer",
    response_model=TransactionDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Transfer money from this wallet to another wallet",
    description="Executes an atomic transfer from the path wallet_id to the receiver_wallet_id with row locking and idempotency protection.",
)
@limiter.limit("20/minute")
def transfer_from_wallet(
    request: Request,
    wallet_id: int,
    transfer_in: TransferRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TransactionDetailResponse:
    return execute_atomic_transfer(
        db=db,
        sender_wallet_id=wallet_id,
        receiver_wallet_id=transfer_in.receiver_wallet_id,
        amount=transfer_in.amount,
        idempotency_key=str(transfer_in.idempotency_key),
        current_user=current_user,
    )


@router.post(
    "/transfer",
    response_model=TransactionDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Direct transfer endpoint specifying both sender and receiver",
    description="Alternative direct transfer endpoint accepting sender_wallet_id and receiver_wallet_id in the request payload.",
)
@limiter.limit("20/minute")
def direct_transfer(
    request: Request,
    transfer_in: DirectTransferRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TransactionDetailResponse:
    return execute_atomic_transfer(
        db=db,
        sender_wallet_id=transfer_in.sender_wallet_id,
        receiver_wallet_id=transfer_in.receiver_wallet_id,
        amount=transfer_in.amount,
        idempotency_key=str(transfer_in.idempotency_key),
        current_user=current_user,
    )


# ============================================================================
# STEP 18 — AUDIT TRAIL / TRANSACTION HISTORY
# ============================================================================

@router.get(
    "/{wallet_id}/transactions",
    response_model=List[TransactionOut],
    summary="Get wallet transaction audit trail",
    description="Retrieves the chronological audit log of all transactions (sent, received, deposited, withdrawn) for the given wallet.",
)
def get_wallet_transactions(
    wallet_id: int,
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(50, ge=1, le=100, description="Limit for pagination"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[TransactionOut]:
    wallet = db.query(Wallet).filter(Wallet.wallet_id == wallet_id).first()
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Wallet {wallet_id} not found.",
        )
    if wallet.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not have permission to view transactions for this wallet.",
        )

    txns = (
        db.query(Transaction)
        .filter(
            (Transaction.sender_wallet_id == wallet_id)
            | (Transaction.receiver_wallet_id == wallet_id)
        )
        .order_by(Transaction.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return txns
