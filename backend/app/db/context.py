from typing import Optional
from fastapi import Depends
from contextvars import ContextVar
import logging

logger = logging.getLogger(__name__)

db_context: ContextVar[Optional[str]] = ContextVar('db_context', default=None)

def get_db_context() -> Optional[str]:
    context = db_context.get()
    logger.debug(f"Getting context: {context}")
    return context

def set_db_context(survey_name: str):
    logger.debug(f"Setting context to: {survey_name}")
    db_context.set(survey_name) 