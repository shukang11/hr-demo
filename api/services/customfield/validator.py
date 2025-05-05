from typing import Dict, Any, Tuple, List
import jsonschema
from jsonschema import ValidationError as JsonSchemaValidationError


class ValidationError(Exception):
    """自定义验证错误，包含详细的错误信息"""

    def __init__(self, errors: List[Dict[str, Any]]):
        self.errors = errors
        message = "; ".join([f"{e['path']}: {e['message']}" for e in errors])
        super().__init__(message)


def validate_value_against_schema(
    schema: Dict[str, Any], value: Dict[str, Any]
) -> Tuple[bool, List[Dict[str, Any]]]:
    """根据JSON Schema验证数据

    Args:
        schema: JSON Schema定义
        value: 要验证的数据

    Returns:
        Tuple[bool, List[Dict[str, Any]]]: (验证是否通过, 错误列表)
    """
    errors = []

    # 创建验证器
    validator = jsonschema.Draft7Validator(schema)

    # 收集错误
    for error in validator.iter_errors(value):
        # 格式化错误路径
        path = ".".join([str(p) for p in error.path]) if error.path else "root"

        # 添加错误信息
        errors.append(
            {
                "path": path,
                "message": error.message,
                "schema_path": ".".join([str(p) for p in error.schema_path]),
            }
        )

    # 如果没有错误，返回验证通过
    return len(errors) == 0, errors


def validate_against_schema(
    schema_definition: Dict[str, Any], value: Dict[str, Any]
) -> None:
    """验证数据是否符合Schema定义，不符合则抛出异常

    Args:
        schema_definition: 完整的Schema定义
        value: 要验证的数据

    Raises:
        ValidationError: 当数据不符合Schema定义时抛出
    """
    # 提取schema部分
    schema = schema_definition.get("schema", {})
    if not schema:
        return

    # 验证数据
    is_valid, errors = validate_value_against_schema(schema, value)

    # 如果验证失败，抛出异常
    if not is_valid:
        raise ValidationError(errors)
