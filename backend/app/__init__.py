import typing
from typing import Any, Dict, Tuple

if typing.TYPE_CHECKING:
    from backend.app.db.database import get_db_conn, init_db
    from backend.app.db.table import create_table
    from backend.app.db.context import get_db_context, set_db_context
    from backend.app.models.base import Survey, QuestionOrField, Response, ResponseModel, DBContents


__all__ = (
    'DBContents',
    'QuestionOrField',
    'Response',
    'ResponseModel',
    'Survey',
    'create_table',
    'get_db_conn',
    'init_db',
    'get_db_context',
    'set_db_context'
)

_dynamic_imports: Dict[str, Tuple[str, str]] = {
    'DBContents': ('backend.app', '.models.base'),
    'QuestionOrField': ('backend.app', '.models.base'),
    'Response': ('backend.app', '.models.base'),
    'ResponseModel': ('backend.app', '.models.base'),
    'Survey': ('backend.app', '.models.base'),
    'create_table': ('backend.app', '.db.table'),
    'get_db_conn': ('backend.app', '.db.database'),
    'init_db': ('backend.app', '.db.database'),
    'get_db_context': ('backend.app', '.db.context'),
    'set_db_context': ('backend.app', '.db.context')
}

def __getattr__(attr_name: str) -> Any:
    dynamic_attr = _dynamic_imports.get(attr_name)
    if dynamic_attr is None:
        raise AttributeError(f"'{__name__}' object has no attribute '{attr_name}'")
    
    package, module_name = dynamic_attr
    from importlib import import_module
    
    if module_name == '__module__':
        return import_module(f'.{attr_name}', package=package)
    else:
        module = import_module(module_name, package=package)
        return getattr(module, attr_name)
    
def __dir__() -> list[str]:
    return list(__all__)