"""CLI entry point for the leadgen tool."""

import click


@click.group()
def main():
    """Organic lead generation automation."""
    pass


@main.command()
def status():
    """Show system status."""
    click.echo("Leadgen system: OK")
