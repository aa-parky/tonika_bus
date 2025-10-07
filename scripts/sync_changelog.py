#!/usr/bin/env python3
"""
Sync GitHub release draft to CHANGELOG.md

This script fetches the latest draft release from GitHub and converts it
to Keep a Changelog format, then adds it to CHANGELOG.md.

Usage:
    python scripts/sync_changelog.py

Requirements:
    pip install requests

Environment Variables:
    GITHUB_TOKEN - GitHub personal access token (optional, but recommended)
"""

import os
import re
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("❌ Error: 'requests' library not installed")
    print("💡 Install with: pip install requests")
    sys.exit(1)


def get_latest_draft_release(repo: str, token: str = None):
    """Fetch latest draft release from GitHub API"""
    url = f"https://api.github.com/repos/{repo}/releases"
    headers = {"Accept": "application/vnd.github.v3+json"}

    if token:
        headers["Authorization"] = f"token {token}"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch releases: {e}")

    releases = response.json()
    drafts = [r for r in releases if r.get("draft", False)]

    if not drafts:
        return None

    return drafts[0]


def convert_github_release_to_changelog(release_body: str, version: str, date: str) -> str:
    """Convert GitHub release format to Keep a Changelog format"""

    # Remove the "Full Changelog" link
    release_body = re.sub(r'\*\*Full Changelog\*\*:.*', '', release_body)

    # Remove "What's Changed" header
    release_body = release_body.replace("## What's Changed", "")

    # Remove Goblin Notes section
    release_body = re.sub(r'## 🧌 Goblin Notes.*', '', release_body, flags=re.DOTALL)

    # Remove installation instructions
    release_body = re.sub(r'---.*', '', release_body, flags=re.DOTALL)

    # Convert emoji headings to Keep a Changelog style
    emoji_map = {
        "### 🎉 Added": "### Added",
        "### 🔄 Changed": "### Changed",
        "### 🐛 Fixed": "### Fixed",
        "### 🗑️ Removed": "### Removed",
        "### 🔒 Security": "### Security",
        "### 📚 Documentation": "### Documentation",
        "### 🧪 Testing": "### Testing",
        "### ⚙️ Internal": "### Internal",
    }

    for emoji_heading, changelog_heading in emoji_map.items():
        release_body = release_body.replace(emoji_heading, changelog_heading)

    # Clean up extra whitespace
    release_body = re.sub(r'\n{3,}', '\n\n', release_body)
    release_body = release_body.strip()

    # Add version header
    changelog_entry = f"## [{version}] - {date}\n\n{release_body}\n"

    return changelog_entry


def update_changelog(new_entry: str, changelog_path: Path):
    """Insert new entry into CHANGELOG.md after [Unreleased]"""

    if not changelog_path.exists():
        print(f"❌ {changelog_path} not found")
        return False

    content = changelog_path.read_text()

    # Find the [Unreleased] section
    unreleased_pattern = r"(## \[Unreleased\]\s*\n)"

    if not re.search(unreleased_pattern, content):
        print("❌ Could not find [Unreleased] section in CHANGELOG.md")
        return False

    # Insert after [Unreleased]
    updated_content = re.sub(
        unreleased_pattern,
        f"\\1\n{new_entry}\n",
        content,
        count=1
    )

    changelog_path.write_text(updated_content)
    return True


def main():
    repo = "aa-parky/tonika_bus"
    changelog_path = Path("CHANGELOG.md")

    # Try to get GitHub token from environment
    token = os.environ.get("GITHUB_TOKEN")

    if not token:
        print("⚠️  No GITHUB_TOKEN found in environment")
        print("💡 Set it with: export GITHUB_TOKEN='your_token_here'")
        print("   Continuing without authentication (rate limits may apply)...\n")

    print(f"🔍 Fetching latest draft release from {repo}...")

    try:
        draft = get_latest_draft_release(repo, token)
    except Exception as e:
        print(f"❌ Error: {e}")
        if not token:
            print("💡 Try setting GITHUB_TOKEN environment variable")
        sys.exit(1)

    if not draft:
        print("❌ No draft release found")
        print("💡 Create a draft release first, or merge some labeled PRs")
        sys.exit(1)

    version = draft["tag_name"].lstrip("v")
    date = draft["created_at"][:10]  # YYYY-MM-DD
    body = draft["body"]

    print(f"📝 Found draft: v{version} ({date})")
    print(f"\n📄 Preview:")
    print("-" * 60)
    preview = body[:500] + "..." if len(body) > 500 else body
    print(preview)
    print("-" * 60)

    # Convert to changelog format
    changelog_entry = convert_github_release_to_changelog(body, version, date)

    # Confirm
    response = input("\n✅ Add this to CHANGELOG.md? [y/N]: ").lower().strip()

    if response != "y":
        print("❌ Aborted")
        sys.exit(0)

    # Update CHANGELOG.md
    if update_changelog(changelog_entry, changelog_path):
        print(f"✅ Updated {changelog_path}")
        print("\n📋 Next steps:")
        print(f"   1. Review changes: git diff {changelog_path}")
        print(f"   2. Update version in pyproject.toml to {version}")
        print(f"   3. Commit: git commit -am 'Release v{version}'")
        print(f"   4. Create tag: git tag v{version}")
        print(f"   5. Push: git push && git push --tags")
        print(f"   6. Publish the draft release on GitHub")
    else:
        print("❌ Failed to update CHANGELOG.md")
        sys.exit(1)


if __name__ == "__main__":
    main()
