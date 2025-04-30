from flask import Flask, Blueprint


def init_app(app: "Flask") -> None:
    from .health import bp as health_bp
    from .auth import bp as auth_bp
    from .position import bp as position_bp
    from .candidate import bp as candidate_bp
    from .company import bp as company_bp  # 导入公司路由蓝图
    from .department import department_bp  # 导入部门路由蓝图
    from .employee import employee_bp  # 导入员工路由蓝图

    api_bp = Blueprint("api", __name__, url_prefix="/api")

    api_bp.register_blueprint(auth_bp)
    api_bp.register_blueprint(position_bp)
    api_bp.register_blueprint(candidate_bp)
    api_bp.register_blueprint(company_bp)  # 注册公司路由蓝图
    api_bp.register_blueprint(department_bp)  # 注册部门路由蓝图
    api_bp.register_blueprint(employee_bp)  # 注册员工路由蓝图

    app.register_blueprint(health_bp)
    app.register_blueprint(api_bp)
