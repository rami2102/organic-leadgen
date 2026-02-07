"""CLI entry point for the leadgen tool."""

import asyncio
import os
import subprocess
from datetime import date
from pathlib import Path

import click

from leadgen.config import load_config
from leadgen.pipeline import LeadgenPipeline

NICHES = ["restaurants", "law firms", "real estate", "dental offices", "hvac", "accounting"]
TOPICS = [
    "how AI agents save money",
    "automating customer service",
    "reducing missed appointments",
    "streamlining operations",
]


@click.group()
def main():
    """Organic lead generation automation."""
    pass


@main.command()
def status():
    """Show system status and configuration."""
    config = load_config()
    click.echo("Leadgen system: OK")
    click.echo(f"  Content model: {config.content_model} (Claude Code CLI)")
    click.echo(f"  Hugo blog: {config.hugo_blog_dir}")
    click.echo(f"  Hashnode: {'configured' if config.hashnode_api_token else 'not set'}")
    click.echo(f"  Dev.to: {'configured' if config.devto_api_key else 'not set'}")
    click.echo(f"  Postiz: {'configured' if config.postiz_api_key else 'not set'}")
    click.echo(f"  ConvertKit: {'configured' if config.convertkit_api_key else 'not set'}")
    click.echo(f"  DataForSEO: {'configured' if config.dataforseo_login else 'not set'}")


@main.command()
@click.option("--niche", required=True, help="Target niche (e.g., restaurants)")
@click.option("--topic", required=True, help="Blog topic")
def generate(niche, topic):
    """Generate a blog post and publish locally."""
    config = load_config()
    pipeline = LeadgenPipeline(
        content_model=config.content_model,
        hugo_blog_dir=config.hugo_blog_dir,
    )

    result = asyncio.run(pipeline.generate_and_publish(niche=niche, topic=topic))
    click.echo(f"Published: {result['title']}")
    click.echo(f"  Path: {result['local_path']}")


@main.command()
@click.option("--niche", required=True, help="Target niche for keywords")
@click.option("--max-difficulty", default=50, help="Max keyword difficulty (0-100)")
def keywords(niche, max_difficulty):
    """Research keywords for a niche."""
    config = load_config()

    if not config.dataforseo_login:
        click.echo("Error: DATAFORSEO_LOGIN not configured. See .env.example")
        return

    from leadgen.seo.keywords import KeywordResearcher

    researcher = KeywordResearcher(
        login=config.dataforseo_login,
        password=config.dataforseo_password,
    )

    results = asyncio.run(
        researcher.get_suggestions(f"ai agents for {niche}")
    )
    filtered = researcher.filter_low_competition(results, max_difficulty)

    click.echo(f"Found {len(filtered)} low-competition keywords for '{niche}':")
    for kw in sorted(filtered, key=lambda x: x["search_volume"], reverse=True)[:20]:
        click.echo(
            f"  [{kw['keyword_difficulty']:2d}] {kw['keyword']} "
            f"({kw['search_volume']:,} searches/mo)"
        )


@main.command()
@click.option("--install", is_flag=True, help="Install the cron job (Mon/Wed/Fri 9am UTC)")
@click.option("--remove", is_flag=True, help="Remove the cron job")
def cron(install, remove):
    """Manage the automated publishing cron job."""
    project_dir = Path(__file__).resolve().parent.parent.parent
    leadgen_bin = subprocess.run(
        ["which", "leadgen"], capture_output=True, text=True
    ).stdout.strip()

    cron_comment = "# leadgen auto-publish"
    cron_line = f"0 9 * * 1,3,5 cd {project_dir} && {leadgen_bin} autopublish >> {project_dir}/cron.log 2>&1 {cron_comment}"

    if remove:
        existing = subprocess.run(
            ["crontab", "-l"], capture_output=True, text=True
        ).stdout
        new_crontab = "\n".join(
            line for line in existing.splitlines()
            if cron_comment not in line
        )
        subprocess.run(["crontab", "-"], input=new_crontab + "\n", text=True)
        click.echo("Cron job removed.")
        return

    if install:
        existing = subprocess.run(
            ["crontab", "-l"], capture_output=True, text=True
        ).stdout
        if cron_comment in existing:
            click.echo("Cron job already installed.")
            return
        new_crontab = existing.rstrip() + "\n" + cron_line + "\n"
        subprocess.run(["crontab", "-"], input=new_crontab, text=True)
        click.echo(f"Cron job installed: Mon/Wed/Fri 9am UTC")
        click.echo(f"  Logs: {project_dir}/cron.log")
        return

    click.echo("Use --install or --remove. See: leadgen cron --help")


@main.command()
@click.option("--niche", default=None, help="Override niche (default: auto-rotate)")
@click.option("--topic", default=None, help="Override topic (default: auto-rotate)")
def publish(niche, topic):
    """Generate a blog post, commit, and push to GitHub now."""
    if not niche:
        day = date.today().timetuple().tm_yday
        niche = NICHES[day % len(NICHES)]
    if not topic:
        day = date.today().timetuple().tm_yday
        topic = TOPICS[day % len(TOPICS)]

    click.echo(f"Publishing: niche={niche}, topic={topic}")

    config = load_config()
    pipeline = LeadgenPipeline(
        content_model=config.content_model,
        hugo_blog_dir=config.hugo_blog_dir,
    )

    result = asyncio.run(pipeline.generate_and_publish(niche=niche, topic=topic))
    click.echo(f"Published: {result['title']}")
    click.echo(f"  Path: {result['local_path']}")

    # Git commit and push
    project_dir = Path(__file__).resolve().parent.parent.parent
    subprocess.run(["git", "add", "blog/content/"], cwd=project_dir)
    diff = subprocess.run(
        ["git", "diff", "--cached", "--quiet"], cwd=project_dir
    )
    if diff.returncode != 0:
        subprocess.run(
            ["git", "commit", "-m", f"content: auto-generated post ({niche})"],
            cwd=project_dir,
        )
        subprocess.run(["git", "push"], cwd=project_dir)
        click.echo("Committed and pushed to GitHub.")
    else:
        click.echo("No new content to commit.")


@main.command()
def autopublish():
    """Auto-generate and git-push a blog post (used by cron). Same as 'publish' with no args."""
    from click.testing import CliRunner
    runner = CliRunner()
    result = runner.invoke(publish, standalone_mode=False)
    if result.output:
        click.echo(result.output, nl=False)
