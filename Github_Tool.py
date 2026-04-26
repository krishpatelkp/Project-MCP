import httpx
from typing import Any
from mcp.server.fastmcp import FastMCP
from datetime import datetime
import asyncio
import os
import shutil

mcp = FastMCP("MCP_Server")

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


async def get_contributors(owner: str, repo: str) -> list:
    url = f"{GITHUB_API}/repos/{owner}/{repo}/contributors"
    data = await make_github_request(url)

    if not data:
        return []

    return [
        f"{c['login']} ({c['contributions']} commits)"
        for c in data[:5]
    ]


def extract_readme_sections(readme: str) -> str:
    if not readme:
        return "No README available"

    lines = readme.split("\n")
    headings = [line for line in lines if line.startswith("#")]

    return "\n".join(headings[:8]) or "No sections found"

def analyze_repo(commits_raw):
    if not commits_raw:
        return "No commit data"

    latest_commit = commits_raw[0]["commit"]["author"]["date"]
    date = datetime.fromisoformat(latest_commit.replace("Z", ""))

    days = (datetime.now() - date).days

    return f"Last Commit: {date} | Status: {'Active' if days < 30 else 'Inactive'}"




@mcp.tool()
async def github_full_report(owner: str, repo: str) -> str:
    """Complete GitHub repo analysis (best tool)."""

    repo_url = f"{GITHUB_API}/repos/{owner}/{repo}"
    commits_url = f"{GITHUB_API}/repos/{owner}/{repo}/commits"

    async def get_readme_raw():
        url = f"{GITHUB_API}/repos/{owner}/{repo}/readme"
        headers = {"Accept": "application/vnd.github.v3.raw"}

        async with httpx.AsyncClient() as client:
            try:
                res = await client.get(url, headers=headers)
                res.raise_for_status()
                return res.text
            except:
                return None

    repo_data, commits_raw, contributors, readme_raw = await asyncio.gather(
        make_github_request(repo_url),
        make_github_request(commits_url),
        get_contributors(owner, repo),
        get_readme_raw()
    )

    if not repo_data:
        return "Repository not found."

    health = analyze_repo(commits_raw)

    readme_sections = extract_readme_sections(readme_raw)

    return f"""
📦 Repo: {repo_data['full_name']}
⭐ Stars: {repo_data['stargazers_count']}
🍴 Forks: {repo_data['forks_count']}
💻 Language: {repo_data['language']}

📊 {health}

👥 Top Contributors:
{"\n".join(contributors) if contributors else "No contributors"}

📘 README Sections:
{readme_sections}
"""


@mcp.tool()
async def extract_clean_text(url: str) -> str:
    """Extract clean readable text from a webpage."""

    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(url, timeout=20.0)
            html = res.text

            import re
            text = re.sub('<script.*?>.*?</script>', '', html, flags=re.DOTALL)
            text = re.sub('<style.*?>.*?</style>', '', text, flags=re.DOTALL)
            text = re.sub('<[^<]+?>', '', text)

            return text.strip()[:2000]

        except:
            return "Failed to extract content"


@mcp.tool()
async def api_debugger(url: str) -> str:
    """Fetch API and return formatted JSON."""

    import json

    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(url, timeout=20.0)
            data = res.json()

            return json.dumps(data, indent=2)[:2000]

        except:
            return "API request failed"



@mcp.tool()
async def analyze_text_advanced(text: str) -> str:
    """Analyze text deeply: length, keywords, structure."""

    from collections import Counter

    words = text.split()
    sentences = [s for s in text.split(".") if s.strip()]

    freq = Counter(words).most_common(5)

    return f"""
Words: {len(words)}
Sentences: {len(sentences)}

Top Keywords:
{", ".join([w for w, _ in freq])}

Preview:
{text[:300]}
"""







# ---------------------------
# 📁 OPTIONAL BASE DIRS
# ---------------------------
FILE_BASE_DIR = None
EXPENSE_BASE_DIR = None

def safe_path(path: str, base_dir: str = None) -> str:
    # If relative path + base dir exists
    if not os.path.isabs(path):
        if base_dir:
            full_path = os.path.abspath(os.path.join(base_dir, path))
        else:
            raise Exception("Full path required or set a base directory first")
    else:
        full_path = os.path.abspath(path)

    blocked_paths = [
        os.path.abspath("C:/Windows"),
        os.path.abspath("C:/Program Files"),
        os.path.abspath("C:/Program Files (x86)"),
        os.path.abspath("C:/System32")
    ]

    if any(full_path.startswith(bp) for bp in blocked_paths):
        raise Exception("Access denied: restricted system directory")

    return full_path

# ---------------------------
# 💰 SAFE GENERAL PATH (For Expense Tracker)
# Blocks only critical Windows folders
# ---------------------------
def safe_general_path(path: str) -> str:
    full_path = os.path.abspath(path)

    blocked_paths = [
        os.path.abspath("C:/Windows"),
        os.path.abspath("C:/Program Files"),
        os.path.abspath("C:/Program Files (x86)"),
        os.path.abspath("C:/System32")
    ]

    if any(full_path.startswith(bp) for bp in blocked_paths):
        raise Exception("Access denied: restricted system directory")

    return full_path

# ---------------------------
# 📁 CREATE FOLDER
# ---------------------------
@mcp.tool()
async def create_folder(path: str) -> str:
    try:
        full_path = safe_path(path, FILE_BASE_DIR)
        os.makedirs(full_path, exist_ok=True)
        return f"Folder created: {full_path}"
    except Exception as e:
        return str(e)


# ---------------------------
# 📄 CREATE FILE
# ---------------------------
@mcp.tool()
async def create_file(path: str, content: str = "") -> str:
    try:
        full_path = safe_path(path, FILE_BASE_DIR)

        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

        return f"File created: {full_path}"
    except Exception as e:
        return str(e)


# ---------------------------
# ✏️ APPEND TO FILE
# ---------------------------
@mcp.tool()
async def append_file(path: str, content: str) -> str:
    try:
        full_path = safe_path(path, FILE_BASE_DIR)

        with open(full_path, "a", encoding="utf-8") as f:
            f.write(content)

        return f"Appended to: {full_path}"
    except Exception as e:
        return str(e)


# ---------------------------
# 📖 READ FILE
# ---------------------------
@mcp.tool()
async def read_file(path: str) -> str:
    try:
        full_path = safe_path(path, FILE_BASE_DIR)

        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()[:3000]

    except Exception as e:
        return str(e)


# ---------------------------
# ✏️ EDIT FILE (OVERWRITE)
# ---------------------------
@mcp.tool()
async def edit_file(path: str, content: str) -> str:
    try:
        full_path = safe_path(path, FILE_BASE_DIR)

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

        return f"File updated: {full_path}"

    except Exception as e:
        return str(e)


# ---------------------------
# 📂 LIST FILES
# ---------------------------
@mcp.tool()
async def list_files(path: str = "") -> str:
    try:
        full_path = safe_path(path, FILE_BASE_DIR)

        files = os.listdir(full_path)

        return "\n".join(files) if files else "Empty folder"

    except Exception as e:
        return str(e)


# ---------------------------
# 🔍 SEARCH FILES
# ---------------------------
@mcp.tool()
async def search_files(keyword: str) -> str:
    results = []

    try:
        search_root = FILE_BASE_DIR if FILE_BASE_DIR else os.getcwd()
        for root, _, files in os.walk(search_root):
            for file in files:
                if keyword.lower() in file.lower():
                    results.append(os.path.join(root, file))

        return "\n".join(results) if results else "No files found"

    except Exception as e:
        return str(e)


# ---------------------------
# 🔎 SEARCH CONTENT IN FILES
# ---------------------------
@mcp.tool()
async def search_content(keyword: str) -> str:
    matches = []

    try:
        search_root = FILE_BASE_DIR if FILE_BASE_DIR else os.getcwd()
        for root, _, files in os.walk(search_root):
            for file in files:
                path = os.path.join(root, file)

                try:
                    with open(path, "r", encoding="utf-8") as f:
                        if keyword.lower() in f.read().lower():
                            matches.append(path)
                except:
                    continue

        return "\n".join(matches) if matches else "No matches found"

    except Exception as e:
        return str(e)


# ---------------------------
# 🔁 RENAME FILE/FOLDER
# ---------------------------
@mcp.tool()
async def rename_path(old_path: str, new_path: str) -> str:
    try:
        old_full = safe_path(old_path, FILE_BASE_DIR)
        new_full = safe_path(new_path, FILE_BASE_DIR)

        os.rename(old_full, new_full)

        return f"Renamed to: {new_full}"

    except Exception as e:
        return str(e)


# ---------------------------
# 🗑 DELETE FILE OR FOLDER
# ---------------------------
@mcp.tool()
async def delete_path(path: str) -> str:
    try:
        full_path = safe_path(path, FILE_BASE_DIR)

        if os.path.isdir(full_path):
            shutil.rmtree(full_path)
        else:
            os.remove(full_path)

        return f"Deleted: {full_path}"

    except Exception as e:
        return str(e)


# ---------------------------
# 📊 FILE INFO
# ---------------------------
@mcp.tool()
async def file_info(path: str) -> str:
    try:
        full_path = safe_path(path, FILE_BASE_DIR)

        stats = os.stat(full_path)

        return f"""
Path: {full_path}
Size: {stats.st_size} bytes
Modified: {stats.st_mtime}
"""

    except Exception as e:
        return str(e)


@mcp.tool()
async def set_file_base_dir(path: str) -> str:
    global FILE_BASE_DIR

    full_path = safe_path(path)

    os.makedirs(full_path, exist_ok=True)

    FILE_BASE_DIR = full_path

    return f"File system base directory set to: {FILE_BASE_DIR}"


@mcp.tool()
async def set_expense_base_dir(path: str) -> str:
    global EXPENSE_BASE_DIR

    full_path = safe_path(path)

    os.makedirs(full_path, exist_ok=True)

    EXPENSE_BASE_DIR = full_path

    return f"Expense tracker base directory set to: {EXPENSE_BASE_DIR}"




def main():
    # Initialize and run the server
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()