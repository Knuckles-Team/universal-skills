import os
import sys
import urllib.request
import urllib.error
import json

def enable_pages(owner, repo):
    token = os.environ.get("GITHUB_ACCESS_TOKEN")
    if not token:
        print("Error: GITHUB_ACCESS_TOKEN environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    url = f"https://api.github.com/repos/{owner}/{repo}/pages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json"
    }
    
    # Configure pages to build from GitHub Actions workflow
    data = json.dumps({"build_type": "workflow"}).encode("utf-8")
    
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req) as response:
            print(f"Successfully enabled GitHub Pages for {owner}/{repo}.")
            print(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode('utf-8')
        if e.code == 409:
            print(f"GitHub Pages might already be enabled or updating. Message: {error_msg}")
        else:
            print(f"Failed to enable GitHub Pages: {e.code} - {error_msg}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python enable_pages.py <owner> <repo_name>")
        sys.exit(1)
    
    enable_pages(sys.argv[1], sys.argv[2])
