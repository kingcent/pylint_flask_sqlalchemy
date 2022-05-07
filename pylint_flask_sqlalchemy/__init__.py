"""
Pylint plugin
"""

from astroid import MANAGER, ClassDef
from astroid.builder import AstroidBuilder

VERSION = "0.2.1"


def register(linter):  # pylint: disable=unused-argument
    """Plugin registration"""


def transform(cls):
    """
    Mimics Flask-SQLAlchemy's _include_sqlalchemy
    """
    if cls.name == "SQLAlchemy":
        import sqlalchemy  # pylint: disable=import-outside-toplevel
        import sqlalchemy.orm  # pylint: disable=import-outside-toplevel

        for module in sqlalchemy, sqlalchemy.orm:
            for key in module.__all__:
                if key == 'Column':
                    source_files = cls.parent.file.split("/")
                    if source_files[-2] == 'flask_sqlalchemy':
                        source_files[-2] = 'sqlalchemy/sql'
                        source_files[-1] = 'operators.py'
                    else:
                        raise BaseException('unknow file name pattern')
                    module = AstroidBuilder(MANAGER).file_build(
                        "/".join(source_files), "sqlalchemy.sql.operators"
                    )
                    column_operators = module.locals.get("ColumnOperators")[0]
                    cls_def = ClassDef(key, None)
                    for method in column_operators.locals.keys():
                        if method.startswith('__'):
                            continue
                        cls_def.locals[method] = column_operators.locals[method]
                    cls.locals[key] = [cls_def]
                else:
                    cls.locals[key] = [ClassDef(key, None)]
    if cls.name == "scoped_session":
        from sqlalchemy.orm import Session  # pylint: disable=import-outside-toplevel

        for key in Session.public_methods:
            cls.locals[key] = [ClassDef(key, None)]


MANAGER.register_transform(ClassDef, transform)
