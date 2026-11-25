from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.config import settings, logger
from app.core.database import Base, engine
from app.core.limiter import limiter
from app.routers import auth_router, wallets_router

# Ensure all database tables exist on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "GlobalPay Wallet Backend API (Complete Production Pipeline: Tasks 1 & 2).\n\n"
        "Core Capabilities:\n"
        "- **User Identity**: Bcrypt hashing & PyJWT bearer authentication\n"
        "- **Multi-Currency Wallets**: Primary & Savings accounts in USD, EUR, GBP, CAD, AUD\n"
        "- **Atomic Money Movement**: Deposits, withdrawals, and race-condition-safe P2P transfers\n"
        "- **Enterprise Resilience**: UUID-based idempotency handling (Stripe/PayPal model)\n"
        "- **Security & Governance**: SlowAPI rate limiting, strict CORS, and persistent audit logs"
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)

# Connect SlowAPI Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Cross-Origin Resource Sharing (CORS - Step 17)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route controllers
app.include_router(auth_router)
app.include_router(wallets_router)


# Global Exception Handling (Step 16)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error on {request.method} {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "detail": "An unexpected server error occurred. Our engineering team has been notified.",
        },
    )


@app.get("/", tags=["General"])
def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "healthy",
        "documentation": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["General"])
def health():
    return {
        "status": "ok",
        "service": "GlobalPay Wallet API",
        "version": settings.VERSION,
    }
