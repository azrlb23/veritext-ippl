import uuid
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.types import TypeDecorator, CHAR, String

try:
    from pgvector.sqlalchemy import Vector
except ImportError:
    class Vector(TypeDecorator):  # type: ignore
        impl = String
        cache_ok = True

        def __init__(self, dim: int = 384, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.dim = dim

        def process_bind_param(self, value, dialect):
            if value is None:
                return None
            if isinstance(value, (list, tuple)):
                return "[" + ",".join(str(float(x)) for x in value) + "]"
            return str(value)

        def process_result_value(self, value, dialect):
            if value is None:
                return None
            if isinstance(value, str):
                cleaned = value.strip("[]")
                return [float(x) for x in cleaned.split(",") if x.strip()]
            return value


class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses CHAR(36).
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == "postgresql":
            if isinstance(value, uuid.UUID):
                return value
            return uuid.UUID(str(value))
        else:
            if isinstance(value, uuid.UUID):
                return str(value)
            return str(uuid.UUID(str(value)))

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(str(value))
