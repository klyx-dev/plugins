#!/usr/bin/env python3
"""Check that the PR author owns any existing plugins being overwritten.

Checks both:
  1. The .owner file on the main branch (durable storage from previous publishes)
  2. The Worker's KV store (realtime owner from current publish sessions)
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
            print(f"⚠️  Repo owner check HTTP {e.code} for {plugin_id}", flush=True)
    except Exception as e:
        print(f"⚠️  Repo owner check error for {plugin_id}: {e}", flush=True)
    return None


def fetch_owner_from_kv(plugin_id: str) -> str | None:
    url = f"{WORKER_URL}/owner/{plugin_id}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "klyx-ci"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return data.get("owner")
    except Exception as e:
        print(f"⚠️  KV owner check error for {plugin_id}: {e}", flush=True)
    return None


def main():
    pr_author = sys.argv[1]
    bundles = sys.argv[2:]

    if not bundles:
        return

    for path in bundles:
        with tarfile.open(path, "r:gz") as tar:
            f = tar.extractfile("plugin.json")
            if f is None:
                print(f"❌ {path}: Missing plugin.json", flush=True)
                sys.exit(1)
            meta = json.loads(f.read())

        plugin_id = meta["id"]

        owner = fetch_owner_from_repo(plugin_id)
        if owner is None:
            owner = fetch_owner_from_kv(plugin_id)

        if owner and owner != pr_author:
            msg = (
                f"❌ {path}: Plugin '{plugin_id}' is owned by '{owner}', "
                f"but PR author is '{pr_author}'. Only the owner can publish updates."
            )
            print(msg, flush=True)
            sys.exit(1)

        if owner:
            print(f"✓ {path}: owner '{owner}' matches PR author", flush=True)
        else:
            print(f"✓ {path}: new plugin (no existing owner)", flush=True)


if __name__ == "__main__":
    main()
