from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.api import auth, expenses, groups, system
from app.core.config import settings
from app.core.logger import setup_logging
from app.core.metrics import MetricsMiddleware


app_logger = setup_logging()


def create_app() -> FastAPI:
    app = FastAPI()
    app.state.logger = app_logger

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.frontend_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(MetricsMiddleware, skip_paths={"/metrics", "/health"})

    app.include_router(system.router)
    app.include_router(groups.router, prefix="/groups", tags=["groups"])
    app.include_router(expenses.router, prefix="/expenses", tags=["expenses"])
    app.include_router(auth.router, prefix="/auth", tags=["auth"])

    return app


app = create_app()


@app.exception_handler(IntegrityError)
def integrity_error_handler(request: Request, exc: IntegrityError):
    return JSONResponse(status_code=400, content={"detail": "Database integrity error"})
