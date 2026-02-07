"""CLI entry point for the leadgen tool."""

import asyncio

import click

from leadgen.config import load_config
from leadgen.pipeline import LeadgenPipeline


@click.group()
def main():
    """Organic lead generation automation."""
    pass


@main.command()
def status():
    """Show system status and configuration."""
    config = load_config()
    click.echo("Leadgen system: OK")
    click.echo(f"  Ollama: {config.ollama_base_url} ({config.ollama_model})")
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
        ollama_url=config.ollama_base_url,
        ollama_model=config.ollama_model,
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
