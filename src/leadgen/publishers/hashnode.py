"""Cross-post articles to Hashnode via GraphQL API."""

import httpx


HASHNODE_API = "https://gql.hashnode.com"


class HashnodePublisher:
    """Publish articles to Hashnode."""

    def __init__(self, api_token: str, publication_id: str):
        self.api_token = api_token
        self.publication_id = publication_id

    async def publish(self, post_data: dict) -> dict:
        mutation = """
        mutation PublishPost($input: PublishPostInput!) {
            publishPost(input: $input) {
                post {
                    id
                    url
                }
            }
        }
        """

        variables = {
            "input": {
                "title": post_data["title"],
                "contentMarkdown": post_data["body"],
                "publicationId": self.publication_id,
                "tags": [{"name": t} for t in post_data.get("tags", [])],
                "slug": post_data.get("slug", ""),
                "originalArticleURL": post_data.get("canonical_url", ""),
            }
        }

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                HASHNODE_API,
                json={"query": mutation, "variables": variables},
                headers={"Authorization": self.api_token},
            )
            resp.raise_for_status()
            data = resp.json()

        post = data["data"]["publishPost"]["post"]
        return {"id": post["id"], "url": post["url"]}
