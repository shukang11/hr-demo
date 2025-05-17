from typing import TYPE_CHECKING, Optional, List
from extensions.ext_database import db
from .base import BaseModel
from sqlalchemy.orm import Mapped, MappedColumn
from sqlalchemy import Integer, String, ForeignKey, JSON, Text

if TYPE_CHECKING:
    from .json_schema import JsonSchemaInDB
    from .department import DepartmentInDB
    from .employee_position import PositionInDB
    from .employee import EmployeeInDB
    from .account_company import AccountCompanyInDB  # 引入 AccountCompanyInDB
    from .account import AccountInDB  # 引入 AccountInDB


class CompanyInDB(BaseModel):
    """公司信息数据库模型
    存储公司基本信息及其与其他实体的关系

    属性:
        name (str): 公司名称，必填
        parent_id (int): 父公司ID，用于树形结构
        extra_value (JSON): 附加JSON格式数据
        extra_schema_id (int): 关联的JSON Schema ID
        extra_schema (JsonSchemaInDB): 关联的JSON Schema对象
        departments (list): 公司部门列表
        positions (list): 公司职位列表
        schemas (list): 公司拥有的JSON Schema列表
        accounts (list[AccountInDB]): 与该公司关联的账户列表 (通过 account_company 表建立的多对多关系)。
        description (str): 公司描述
        parent (CompanyInDB): 父公司对象
        subsidiaries (list): 子公司列表
    """

    __tablename__ = "company"  # 表名

    name: Mapped[str] = MappedColumn(
        String(255),
        nullable=False,  # 不允许为空，公司必须有名称
        comment="公司名称",
    )
    extra_value: Mapped[Optional[dict]] = MappedColumn(
        JSON,
        nullable=True,  # 允许为空，附加数据是可选的
        comment="附加JSON格式数据",
    )
    extra_schema_id: Mapped[Optional[int]] = MappedColumn(
        Integer,
        ForeignKey("json_schemas.id"),
        nullable=True,  # 允许为空，可以没有关联的JSON Schema
        comment="关联的JSON Schema ID",
    )
    description: Mapped[Optional[str]] = MappedColumn(
        Text,
        nullable=True,
        comment="公司描述",
    )
    parent_id: Mapped[Optional[int]] = MappedColumn(
        Integer,
        ForeignKey("company.id"),
        nullable=True,  # 允许为空，表示顶级公司没有父公司
        comment="父公司ID",
    )

    # 关系定义
    extra_schema: Mapped["JsonSchemaInDB"] = db.relationship(
        "JsonSchemaInDB",
        foreign_keys=[extra_schema_id],  # 指定外键
    )  # type: ignore
    departments: Mapped[list["DepartmentInDB"]] = db.relationship(
        "DepartmentInDB",
        back_populates="company",  # 与DepartmentInDB中的company属性相对应
    )  # type: ignore
    positions: Mapped[list["PositionInDB"]] = db.relationship(
        "PositionInDB",
        back_populates="company",  # 与PositionInDB中的company属性相对应
    )  # type: ignore

    members: Mapped[list["EmployeeInDB"]] = db.relationship(
        "EmployeeInDB",
        secondary="employee_position",  # 关联表
        back_populates="companies",  # 与EmployeeInDB中的companies属性相对应
    )  # type: ignore

    # 添加与 AccountCompanyInDB 的一对多关系
    account_companies: Mapped[list["AccountCompanyInDB"]] = db.relationship(
        "AccountCompanyInDB",
        back_populates="company",  # 与 AccountCompanyInDB.company 对应
        cascade="all, delete-orphan",
        overlaps="accounts",  # 与 accounts 关系重叠
    )  # type: ignore
    # 定义与 AccountInDB 的多对多关系，通过 account_company 表
    # secondary 参数指定了连接（中间）表
    # back_populates 指定了在 AccountInDB 模型中反向关联的属性名 (companies)
    accounts: Mapped[List["AccountInDB"]] = db.relationship(
        "AccountInDB",
        secondary="account_company",  # 指定中间表名
        back_populates="companies",  # 指向 AccountInDB.companies
        overlaps="account_companies",  # 与 account_companies 关系重叠
    )  # type: ignore

    # 添加公司拥有的所有JSON Schema
    schemas: Mapped[list["JsonSchemaInDB"]] = db.relationship(
        "JsonSchemaInDB",
        foreign_keys="JsonSchemaInDB.company_id",
        back_populates="company",  # 与JsonSchemaInDB中的company属性对应
        cascade="all, delete-orphan",  # 当公司被删除时，级联删除其所有Schema
    )  # type: ignore

    # 添加父公司和子公司的自引用关系
    parent: Mapped[Optional["CompanyInDB"]] = db.relationship(
        "CompanyInDB",
        remote_side=lambda: [CompanyInDB.id],
        back_populates="subsidiaries",
        foreign_keys=[parent_id],
        uselist=False,  # 一个公司只有一个父公司
    )  # type: ignore
    subsidiaries: Mapped[list["CompanyInDB"]] = db.relationship(
        "CompanyInDB",
        back_populates="parent",
        foreign_keys=[parent_id],
        cascade="all, delete-orphan",  # 当父公司被删除时，级联删除其所有子公司
    )  # type: ignore

    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        parent_id: Optional[int] = None,
        extra_schema_id: Optional[int] = None,
        extra_value: Optional[dict] = None,
    ) -> None:
        """初始化公司信息模型

        Args:
            name (str): 公司名称
            description (Optional[str]): 公司描述
            parent_id (Optional[int]): 父公司ID
            extra_value (Optional[dict]): 附加JSON格式数据
            extra_schema_id (Optional[int]): 关联的JSON Schema ID
        """
        super().__init__()
        self.name = name
        self.description = description
        self.parent_id = parent_id
        self.extra_value = extra_value
        self.extra_schema_id = extra_schema_id
