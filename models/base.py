from datetime import datetime
from extensions.ext_database import db


class BaseModel(db.Model):
    """SQLAlchemy 基础模型类
    为所有数据库模型提供通用字段和功能

    Attributes:
        id (int): 主键ID，自增
        created_at (datetime): 记录创建时间，自动设置为当前时间
        updated_at (datetime): 记录更新时间，创建时和更新时自动设置为当前时间
    """
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 