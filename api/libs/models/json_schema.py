from typing import TYPE_CHECKING, Optional
from sqlalchemy.orm import Mapped, relationship, MappedColumn
from sqlalchemy import String, JSON, Integer, ForeignKey, Enum
import enum
from extensions.ext_database import db
from .base import BaseModel

if TYPE_CHECKING:
    from .company import CompanyInDB


class SchemaEntityType(str, enum.Enum):
    """定义Schema适用的实体类型"""

    EMPLOYEE = "employee"  # 员工
    CANDIDATE = "candidate"  # 候选人
    COMPANY = "company"  # 公司
    DEPARTMENT = "department"  # 部门
    POSITION = "position"  # 职位
    GENERAL = "general"  # 通用


class JsonSchemaInDB(BaseModel):
    """JSON Schema 数据库模型，用于存储和管理 JSON 数据结构模式

    属性:
        name (str): Schema 名称，必填
        schema (JSON): JSON Schema 定义，必填
        entity_type (SchemaEntityType): Schema适用的实体类型
        is_system (bool): 是否为系统预设Schema
        version (int): Schema版本号
        parent_schema_id (int): 父Schema ID，用于版本管理
        company_id (int): 所属公司 ID，可选
        remark (str): 备注信息，可选
        company (CompanyInDB): 关联的公司对象
        ui_schema (JSON): UI展示相关的配置
    """

    __tablename__ = "json_schemas"

    id: Mapped[int] = MappedColumn(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="ID",
    )
    name: Mapped[str] = MappedColumn(String(255), nullable=False, comment="Schema 名称")
    schema: Mapped[dict] = MappedColumn(
        JSON, nullable=False, comment="JSON Schema 定义"
    )
    entity_type: Mapped[SchemaEntityType] = MappedColumn(
        Enum(SchemaEntityType),
        nullable=False,
        default=SchemaEntityType.GENERAL,
        comment="Schema适用的实体类型",
    )
    is_system: Mapped[bool] = MappedColumn(
        db.Boolean, default=False, nullable=False, comment="是否为系统预设Schema"
    )
    version: Mapped[int] = MappedColumn(
        Integer, default=1, nullable=False, comment="Schema版本号"
    )
    parent_schema_id: Mapped[Optional[int]] = MappedColumn(
        Integer,
        ForeignKey("json_schemas.id"),
        nullable=True,
        comment="父Schema ID，用于版本管理",
    )
    company_id: Mapped[Optional[int]] = MappedColumn(
        Integer, ForeignKey("company.id"), nullable=True, comment="所属公司ID"
    )
    remark: Mapped[Optional[str]] = MappedColumn(
        String(255),
        nullable=True,  # 允许为空，备注是可选的
        comment="备注信息",
    )
    ui_schema: Mapped[Optional[dict]] = MappedColumn(
        JSON, nullable=True, comment="UI展示相关的配置"
    )

    # 关系定义
    company: Mapped["CompanyInDB"] = relationship(
        "CompanyInDB", foreign_keys=[company_id], back_populates="schemas"
    )
    parent_schema: Mapped["JsonSchemaInDB"] = relationship(
        "JsonSchemaInDB",
        remote_side=lambda: [JsonSchemaInDB.id],  # 使用lambda延迟计算
        backref="child_schemas",
    )

    def __init__(
        self,
        name: str,
        schema: dict,
        entity_type: SchemaEntityType,
        ui_schema: Optional[dict],
        company_id: Optional[int] = None,
        is_system: bool = False,
        remark: Optional[str] = None,
        parent_schema_id: Optional[int] = None,
        version: int = 1,
    ) -> None:
        """初始化JsonSchemaInDB实例

        Args:
            name (str): Schema名称
            schema (dict): JSON Schema定义
            entity_type (SchemaEntityType): Schema适用的实体类型
            ui_schema (Optional[dict]): UI展示相关的配置
            company_id (Optional[int]): 所属公司ID
            is_system (bool): 是否为系统预设Schema
            remark (Optional[str]): 备注信息
            parent_schema_id (Optional[int]): 父Schema ID，用于版本管理
            version (int): Schema版本号
        """
        super().__init__()
        self.name = name
        self.schema = schema
        self.entity_type = entity_type
        self.ui_schema = ui_schema
        self.company_id = company_id
        self.is_system = is_system
        self.remark = remark
        self.parent_schema_id = parent_schema_id
        self.version = version
