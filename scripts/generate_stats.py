import json
import os
import urllib.request
from collections import Counter
from pathlib import Path

USERNAME = "saatwiksharma07"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
API = "https://api.github.com"


def get_json(url):
    request = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "saatwiksharma07-profile-stats",
        "Authorization": f"Bearer {TOKEN}" if TOKEN else "",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def esc(value):
    return (str(value)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def card_svg(stats):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="495" height="195" viewBox="0 0 495 195" role="img" aria-label="GitHub statistics for {USERNAME}">
<rect width="495" height="195" rx="10" fill="#0d1117" stroke="#30363d"/>
<text x="28" y="38" fill="#f0f6fc" font-family="Arial, sans-serif" font-size="20" font-weight="700">GitHub Stats</text>
<text x="28" y="76" fill="#8b949e" font-family="Arial, sans-serif" font-size="13">Public repositories</text>
<text x="28" y="101" fill="#58a6ff" font-family="Arial, sans-serif" font-size="22" font-weight="700">{stats['repos']}</text>
<text x="190" y="76" fill="#8b949e" font-family="Arial, sans-serif" font-size="13">Followers</text>
<text x="190" y="101" fill="#58a6ff" font-family="Arial, sans-serif" font-size="22" font-weight="700">{stats['followers']}</text>
<text x="340" y="76" fill="#8b949e" font-family="Arial, sans-serif" font-size="13">Stars earned</text>
<text x="340" y="101" fill="#58a6ff" font-family="Arial, sans-serif" font-size="22" font-weight="700">{stats['stars']}</text>
<line x1="28" y1="126" x2="467" y2="126" stroke="#30363d"/>
<text x="28" y="155" fill="#8b949e" font-family="Arial, sans-serif" font-size="12">Updated automatically by GitHub Actions</text>
<text x="28" y="176" fill="#8b949e" font-family="Arial, sans-serif" font-size="12">github.com/{USERNAME}</text>
</svg>'''


def languages_svg(languages):
    rows = []
    y = 56
    for language, amount in languages[:6]:
        rows.append(f'''<text x="28" y="{y}" fill="#f0f6fc" font-family="Arial, sans-serif" font-size="13">{esc(language)}</text><text x="360" y="{y}" fill="#8b949e" font-family="Arial, sans-serif" font-size="13">{amount:.1f}%</text>''')
        y += 22
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="495" height="195" viewBox="0 0 495 195" role="img" aria-label="Top programming languages for {USERNAME}">
<rect width="495" height="195" rx="10" fill="#0d1117" stroke="#30363d"/>
<text x="28" y="34" fill="#f0f6fc" font-family="Arial, sans-serif" font-size="20" font-weight="700">Top Languages</text>
{''.join(rows)}
</svg>'''


user = get_json(f"{API}/users/{USERNAME}")
repos = get_json(f"{API}/users/{USERNAME}/repos?per_page=100&type=owner&sort=updated")

# Aggregate actual language byte counts from every public owned repository.
language_bytes = Counter()
for repo in repos:
    if repo.get("fork"):
        continue
    try:
        data = get_json(repo["languages_url"])
        language_bytes.update(data)
    except Exception:
        # Keep the generator resilient if one repository's language endpoint fails.
        continue

stars = sum(repo.get("stargazers_count", 0) for repo in repos)
total_bytes = sum(language_bytes.values())
languages = []
if total_bytes:
    languages = sorted(
        ((name, value / total_bytes * 100) for name, value in language_bytes.items()),
        key=lambda item: item[1],
        reverse=True,
    )

stats = {
    "repos": user.get("public_repos", 0),
    "followers": user.get("followers", 0),
    "stars": stars,
}

output = Path("assets")
output.mkdir(parents=True, exist_ok=True)
(output / "github-stats.svg").write_text(card_svg(stats), encoding="utf-8")
(output / "top-languages.svg").write_text(languages_svg(languages), encoding="utf-8")
