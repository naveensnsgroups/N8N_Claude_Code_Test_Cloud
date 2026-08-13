"""
FastAPI application main entry point.
Equivalent to Express server.js with middleware and routes setup.
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager
from typing import Callable
import logging

from config import get_settings
from database import connect_to_mongo, close_mongo_connection
from routes import employee_routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()

# ─── Rate Limiter ─────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)


# ─── Lifespan Events ──────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application startup and shutdown events.
    Connect to MongoDB on startup, close on shutdown.
    """
    # Startup
    logger.info('Starting FastAPI application...')
    try:
        await connect_to_mongo()
        logger.info(f'Server running in {settings.environment} mode on port {settings.port}')
    except Exception as e:
        logger.error(f'Failed to connect to MongoDB: {str(e)}')
        raise

    yield

    # Shutdown
    logger.info('Shutting down FastAPI application...')
    await close_mongo_connection()


# ─── FastAPI App Initialization ────────────────────────────────────────────
app = FastAPI(
    title=settings.api_title,
    description="MERN Stack Personal Details App - FastAPI Backend",
    version=settings.api_version,
    lifespan=lifespan
)

# Add rate limiter to app
app.state.limiter = limiter


def _rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Handle rate limit exceeded errors."""
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            'success': False,
            'message': 'Too many requests, please try again later.'
        }
    )


app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ─── Security Middleware ──────────────────────────────────────────────────
# Trusted Host Middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=['*']  # Allow all hosts (adjust in production)
)

# CORS Middleware
# Parse allowed origins from config
allowed_origins = [
    url.strip().rstrip('/') for url in settings.client_url.split(',')
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if '*' not in allowed_origins else ['*'],
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'PUT', 'DELETE'],
    allow_headers=['Content-Type'],
)


# ─── Middleware for Request Logging and Error Handling ──────────────────
@app.middleware('http')
async def log_requests(request: Request, call_next: Callable):
    """
    Middleware to log all incoming requests.
    """
    try:
        response = await call_next(request)
        logger.info(
            f'[{response.status_code}] {request.method} {request.url.path}'
        )
        return response
    except Exception as e:
        logger.error(
            f'[ERROR] {request.method} {request.url.path} — {str(e)}'
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                'success': False,
                'message': (
                    'Internal Server Error'
                    if settings.environment == 'production'
                    else str(e)
                )
            }
        )


# ─── Global Exception Handler ─────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for unhandled exceptions.
    """
    logger.error(
        f'[UNHANDLED ERROR] {request.method} {request.url.path} — {str(exc)}'
    )

    status_code = getattr(exc, 'status_code', status.HTTP_500_INTERNAL_SERVER_ERROR)
    message = (
        'Internal Server Error'
        if settings.environment == 'production'
        else str(exc)
    )

    return JSONResponse(
        status_code=status_code,
        content={'success': False, 'message': message}
    )


# ─── Routes ───────────────────────────────────────────────────────────────

# Include employee routes with rate limiting
app.include_router(
    employee_routes.router,
    prefix='/api/employees',
    tags=['employees']
)


# Health check endpoint
@app.get('/', tags=['health'])
async def health_check():
    """Health check endpoint."""
    return {'success': True, 'message': 'Personal Details API is running.'}


# 404 Handler
@app.api_route('/{path_name:path}', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
async def catch_all(path_name: str):
    """Catch all undefined routes and return 404."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={'success': False, 'message': 'Route not found'}
    )


# ─── Development Server ────────────────────────────────────────────────────
if __name__ == '__main__':
    import uvicorn

    uvicorn.run(
        'main:app',
        host=settings.host,
        port=settings.port,
        reload=settings.environment == 'development'
    )
