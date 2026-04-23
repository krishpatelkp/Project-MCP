import httpx
from typing import Any
from mcp.server.fastmcp import FastMCP
from datetime import datetime

mcp = FastMCP("github-tools")

GITHUB_API = "https://api.github.com"


async def make_github_request(url: str) -> dict[str, Any] | None:
    headers = {
        "Accept": "application/vnd.github+json",
        # Optional but recommended:
        # "Authorization": "Bearer YOUR_TOKEN"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None


def format_repo(data: dict) -> str:
    return f"""
Repository: {data.get("name")}
Owner: {data.get("owner", {}).get("login")}
Stars: {data.get("stargazers_count")}
Forks: {data.get("forks_count")}
Language: {data.get("language")}
URL: {data.get("html_url")}
Description: {data.get("description")}
"""


@mcp.tool()
async def get_github_repo(owner: str, repo: str) -> str:
    """Fetch GitHub repository details.

    Args:
        owner: Repository owner (e.g. facebook)
        repo: Repository name (e.g. react)
    """

    url = f"{GITHUB_API}/repos/{owner}/{repo}"
    data = await make_github_request(url)

    if not data:
        return "Unable to fetch repository."

    return format_repo(data)


async def get_readme(owner: str, repo: str) -> str:
    url = f"{GITHUB_API}/repos/{owner}/{repo}/readme"

    headers = {"Accept": "application/vnd.github.v3.raw"}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.text[:800]  # limit size
        except Exception:
            return "README not available."


async def get_commits(owner: str, repo: str) -> list:
    url = f"{GITHUB_API}/repos/{owner}/{repo}/commits"

    data = await make_github_request(url)

    if not data:
        return []

    return [
        f"{c['commit']['author']['name']}: {c['commit']['message']}"
        for c in data[:5]
    ]


@mcp.tool()
async def github_repo_tool(owner: str, repo: str) -> str:
    """Get detailed GitHub repo info with README and commits."""

    repo_data = await make_github_request(f"{GITHUB_API}/repos/{owner}/{repo}")

    if not repo_data:
        return "Repository not found."

    readme = await get_readme(owner, repo)
    commits = await get_commits(owner, repo)

    return f"""
{format_repo(repo_data)}

--- README ---
{readme}

--- Recent Commits ---
{"\n".join(commits)}
"""


def analyze_repo(commits):
    if not commits:
        return "No commit data"

    latest_commit = commits[0]["commit"]["author"]["date"]
    date = datetime.fromisoformat(latest_commit.replace("Z", ""))

    return f"""
Last Commit: {date}
Status: {"Active" if (datetime.now() - date).days < 30 else "Inactive"}
"""


@mcp.tool()
async def search_github_repos(query: str) -> str:
    url = f"https://api.github.com/search/repositories?q={query}"
    data = await make_github_request(url)

    if not data:
        return "Search failed"

    results = data["items"][:5]

    return "\n".join([
        f"{repo['full_name']} ⭐ {repo['stargazers_count']}"
        for repo in results
    ])




def main():
    # Initialize and run the server
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()