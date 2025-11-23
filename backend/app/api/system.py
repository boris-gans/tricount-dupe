from logging import Logger

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.logger import get_request_logger
from app.core.metrics import build_metrics_response
from app.db.session import get_db


router = APIRouter(tags=["system"])


@router.get("/health")
def health(
    db: Session = Depends(get_db),
    logger: Logger = Depends(get_request_logger),
):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok"}
    except SQLAlchemyError:
        logger.error("database health check failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        )


@router.get("/metrics")
def metrics():
    return build_metrics_response()
