from extensions.ext_database import db
from .base import BaseModel
from sqlalchemy.orm import Mapped

class JsonSchemaInDB(BaseModel):
    """JSON Schema database model for storing and managing JSON data structure schemas

    Attributes:
        name (str): Schema name, required
        schema (JSON): JSON Schema definition, required
    """
    __tablename__ = 'json_schemas'

    name: Mapped[str] = db.Column(db.String(255), nullable=False)
    schema: Mapped[dict] = db.Column(db.JSON, nullable=False) 