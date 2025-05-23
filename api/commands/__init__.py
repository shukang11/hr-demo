from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flask import Flask


def register_commands(app: "Flask") -> None:
    from . import init_dev_data, upgrade_db, update_employee_schemas

    app.cli.add_command(upgrade_db.command)
    app.cli.add_command(init_dev_data.command)
    app.cli.add_command(update_employee_schemas.update_employee_schemas)
