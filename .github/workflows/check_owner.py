#!/usr/bin/env python3
"""Check that the PR author owns any existing plugins being overwritten.

Checks both:
  1. The .owner file on the main branch (durable storage from previous publishes)
  2. The Worker's KV store (realtime owner from current publish sessions)
Reports all issues found before exiting.
"""

import json
import sys
import tarfile
import urllib.request

REPO = "klyx-dev/plugins"
BRANCH = "main"
WORKER_URL = "https://plugins.klyx.workers.dev"


def fetch_owner_from_repo(plugin_id: str) -> str | None:
    url = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/plugins/{plugin_id}/.owner"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "klyx-ci"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read().decode().strip()
    except urllib.error.HTTPError as e:
        if e.code != 404:
            print(f"⚠️  Could not check repo owner for {plugin_id}: HTTP {e.code}", flush=True)
    except Exception as e:
        print(f"⚠️  Could not check repo owner for {plugin_id}: {e}", flush=True)
    return None


def fetch_owner_from_kv(plugin_id: str) -> str | None:
    url = f"{WORKER_URL}/owner/{plugin_id}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "klyx-ci"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return data.get("owner")
    except Exception as e:
        print(f"⚠️  Could not check KV owner for {plugin_id}: {e}", flush=True)
    return None


def main():
    pr_author = sys.argv[1]
    bundles = sys.argv[2:]

    if not bundles:
        return

    exit_code = 0

    for path in bundles:
        try:
            with tarfile.open(path, "r:gz") as tar:
                f = tar.extractfile("plugin.json")
                if f is None:
                    print(f"❌ {path}: Missing plugin.json — cannot check ownership", flush=True)
                    exit_code = 1
                    continue
                meta = json.loads(f.read())
        except Exception as e:
            print(f"❌ {path}: Cannot read bundle — cannot check ownership: {e}", flush=True)
            exit_code = 1
            continue

        plugin_id = meta.get("id")
        if not plugin_id:
            print(f"❌ {path}: plugin.json missing 'id' — cannot check ownership", flush=True)
            exit_code = 1
            continue

        owner = fetch_owner_from_repo(plugin_id)
        if owner is None:
            owner = fetch_owner_from_kv(plugin_id)

        if owner and owner != pr_author:
            print(
                f"❌ {path}: Plugin '{plugin_id}' is owned by '{owner}', "
                f"but PR author is '{pr_author}'. Only the owner can publish updates.",
                flush=True
            )
            exit_code = 1
        elif owner:
            print(f"✓ {path}: owner '{owner}' matches PR author", flush=True)
        else:
            print(f"✓ {path}: new plugin (no existing owner)", flush=True)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
