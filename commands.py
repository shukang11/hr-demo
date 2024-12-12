from typing import TYPE_CHECKING

import click

if TYPE_CHECKING:
    from flask import Flask


@click.command("upgrade-db", help="Upgrade the database")
def upgrade_db():
    click.echo("Preparing database migration...")
    try:
        import flask_migrate

        flask_migrate.upgrade()
        click.echo(click.style("Database migration successful!", fg="green"))
    except Exception as e:
        click.echo(f"Failed to execute database migration: {e}")


def register_commands(app: "Flask") -> None:
    app.cli.add_command(upgrade_db)