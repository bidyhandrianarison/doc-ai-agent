"""Ingestion utilities for downloading and extracting markdown repository data.

This module fetches a GitHub repository archive, parses markdown/MDX files,
extracts frontmatter metadata, and returns a list of document dictionaries.
"""

import io
import zipfile
import frontmatter
import requests
from minsearch import Index

def read_repo_data(repo_owner, repo_name, branch):
    """Download and parse markdown documents from a GitHub repository branch.

    Args:
        repo_owner: GitHub owner (user or organization).
        repo_name: GitHub repository name.
        branch: Branch name to download.

    Returns:
        A list of dictionaries containing frontmatter fields and content.

    Raises:
        RuntimeError: If repository download fails.
    """
    prefix = "https://codeload.github.com"
    url = f"{prefix}/{repo_owner}/{repo_name}/zip/refs/heads/{branch}"
    resp = requests.get(url, timeout=30)

    if resp.status_code != 200:
        raise RuntimeError(f"Failed to download repository: {resp.status_code}")

    repository_data = []
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        for file_info in zf.infolist():
            filename = file_info.filename
            filename_lower = filename.lower()

            if not (filename_lower.endswith(".md") or filename_lower.endswith(".mdx")):
                continue

            try:
                with zf.open(file_info) as f_in:
                    content = f_in.read().decode("utf-8", errors="ignore")
                    post = frontmatter.loads(content)
                    data = post.to_dict()
                    # Drop zip root directory (e.g. repo-main/) for cleaner paths.
                    _, repo_filename = filename.split("/", maxsplit=1)
                    data["filename"] = repo_filename
                    repository_data.append(data)
            except Exception as exc:
                print(f"Error processing {filename}: {exc}")

    return repository_data

def index_data(repo_owner, repo_name, branch="main", doc_filter=None):
    """Run ingestion + filtering + text indexing in one place.

    Args:
        repo_owner: GitHub owner.
        repo_name: GitHub repository name.
        branch: Git branch to ingest.
        doc_filter: Optional callable(doc) -> bool.

    Returns:
        A fitted minsearch.Index instance.
    """
    docs = read_repo_data(repo_owner=repo_owner, repo_name=repo_name, branch=branch)

    if doc_filter is not None:
        docs = [doc for doc in docs if doc_filter(doc)]

    index = Index(text_fields=["content", "filename"])
    index.fit(docs)
    return index