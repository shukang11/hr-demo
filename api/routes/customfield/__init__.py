"""
自定义字段相关路由模块
包含Schema定义、值管理和高级功能的API端点
"""

from flask import Blueprint

# 创建自定义字段相关的蓝图
bp = Blueprint("customfield", __name__, url_prefix="/customfield")

# 导入各个子模块，注册路由到蓝图
from . import schema, value, advanced  # noqa: E402, F401

# 导出蓝图供app注册
__all__ = ["bp"]
