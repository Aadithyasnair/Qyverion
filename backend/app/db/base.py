from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):
    """
    Modern SQLAlchemy 2.x Declarative Base class.
    All database models will inherit from this class.
    Automatically generates lowercase tablenames from class names.
    """
    @declared_attr.directive
    def __tablename__(cls) -> str:
        # e.g., UserAccount -> useraccount
        return cls.__name__.lower()
