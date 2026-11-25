from decimal import Decimal
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.core.config import settings, logger
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.limiter import limiter
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.models.wallet import Wallet
from app.schemas.user import UserCreate, UserOut, LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/signup",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Registers a new user, hashes the password with bcrypt, and automatically creates a default Primary USD wallet.",
)
@limiter.limit("15/minute")
def signup(request: Request, user_in: UserCreate, db: Session = Depends(get_db)) -> UserOut:
    # 1. Check if email already registered
    existing_user = db.query(User).filter(User.email == user_in.email.lower().strip()).first()
    if existing_user:
        logger.warning(f"Registration rejected: duplicate email '{user_in.email}'")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists.",
        )

    # 2. Hash password and create User
    hashed_pwd = hash_password(user_in.password)
    db_user = User(
        full_name=user_in.full_name.strip(),
        email=user_in.email.lower().strip(),
        phone_number=user_in.phone_number.strip() if user_in.phone_number else None,
        country=user_in.country.strip(),
        password_hash=hashed_pwd,
        is_verified=False,
    )
    db.add(db_user)
    db.flush()

    # 3. Create default Primary wallet for the user
    primary_wallet = Wallet(
        user_id=db_user.user_id,
        currency="USD",
        balance=Decimal("0.00"),
        wallet_type="Primary",
    )
    db.add(primary_wallet)
    db.commit()
    db.refresh(db_user)

    logger.info(f"New user registered: User ID {db_user.user_id} ({db_user.email}) with Primary USD wallet {primary_wallet.wallet_id}")
    return db_user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate user and obtain JWT token",
    description="Validates email and password, then issues a signed JWT access token. Rate limited against brute-force attacks.",
)
@limiter.limit("10/minute")
def login(request: Request, login_in: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.query(User).filter(User.email == login_in.email.lower().strip()).first()
    if not user or not verify_password(login_in.password, user.password_hash):
        logger.warning(f"Failed login attempt for email: {login_in.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    expires_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    access_token = create_access_token(
        subject=user.user_id,
        expires_delta=timedelta(minutes=expires_minutes),
        extra_claims={"email": user.email},
    )

    logger.info(f"User login successful: User ID {user.user_id} ({user.email})")
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_minutes * 60,
    )


@router.get(
    "/me",
    response_model=UserOut,
    summary="Get current user profile",
    description="Returns the profile of the currently authenticated user.",
)
def get_me(current_user: User = Depends(get_current_user)) -> UserOut:
    return current_user
