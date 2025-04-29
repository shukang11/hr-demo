
import click

@click.command("upgrade-db", help="Upgrade the database")
def command():
    click.echo("Preparing database migration...")
    try:
        import flask_migrate

        flask_migrate.upgrade()
        click.echo(click.style("Database migration successful!", fg="green"))
    except Exception as e:
        click.echo(f"Failed to execute database migration: {e}")

