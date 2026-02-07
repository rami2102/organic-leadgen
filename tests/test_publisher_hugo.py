import os
from pathlib import Path
from leadgen.publishers.hugo import HugoPublisher


def test_hugo_publisher_creates_post(tmp_path):
    blog_dir = tmp_path / "blog"
    content_dir = blog_dir / "content" / "posts"
    content_dir.mkdir(parents=True)

    publisher = HugoPublisher(blog_dir=str(blog_dir))

    post_data = {
        "title": "5 Ways AI Agents Save Restaurants Money",
        "slug": "5-ways-ai-agents-save-restaurants-money",
        "meta_description": "Discover how AI agents help restaurants cut costs.",
        "body": "# 5 Ways AI Agents Save Restaurants Money\n\nContent here...",
        "tags": ["ai", "restaurants", "automation"],
    }

    filepath = publisher.publish(post_data)

    assert filepath.exists()
    content = filepath.read_text()
    assert "title:" in content
    assert "5 Ways AI Agents Save Restaurants Money" in content
    assert "description:" in content
    assert "Content here..." in content


def test_hugo_publisher_generates_valid_frontmatter(tmp_path):
    blog_dir = tmp_path / "blog"
    content_dir = blog_dir / "content" / "posts"
    content_dir.mkdir(parents=True)

    publisher = HugoPublisher(blog_dir=str(blog_dir))

    post_data = {
        "title": "Test Post",
        "slug": "test-post",
        "meta_description": "A test post.",
        "body": "Body content.",
        "tags": ["test"],
    }

    filepath = publisher.publish(post_data)
    content = filepath.read_text()

    assert content.startswith("---\n")
    assert content.count("---") >= 2
