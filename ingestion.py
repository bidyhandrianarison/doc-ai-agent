"""Ingestion utilities for downloading and extracting markdown repository data.

This module fetches a GitHub repository archive, parses markdown/MDX files,
extracts frontmatter metadata, and returns a list of document dictionaries.
"""

import io
import json
import zipfile

import frontmatter
import requests

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
                    data["filename"] = filename
                    repository_data.append(data)
            except Exception as exc:
                print(f"Error processing {filename}: {exc}")

    return repository_data


def main():
    """Run ingestion and persist raw repository documents to JSON."""
    langchain_repo = read_repo_data("langchain-ai", "langchain", "master")
    print(f"Langchain documents: {len(langchain_repo)}")
    with open("data/raw_docs.json", "w", encoding="utf-8") as f_out:
        json.dump(langchain_repo, f_out, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()