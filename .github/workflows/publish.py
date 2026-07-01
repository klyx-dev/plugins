#!/usr/bin/env python3
"""Validate a .klyx bundle and publish it to the registry."""

import json
import shutil
import tarfile
import urllib.request
from pathlib import Path

PLUGINS_DIR = Path("plugins")
INCOMING_DIR = Path("incoming")
WORKER_URL = "https://plugins.klyx.workers.dev"


def get_owner_for(plugin_id: str) -> str | None:
    url = f"{WORKER_URL}/owner/{plugin_id}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "klyx-ci"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return data.get("owner")
    except Exception:
        return None


def extract_plugin_json(tar: tarfile.TarFile) -> dict:
    try:
        f = tar.extractfile("plugin.json")
        if f is None:
            raise ValueError("plugin.json not found in bundle")
        return json.loads(f.read())
    except KeyError:
        raise ValueError("plugin.json not found in bundle")


def validate_meta(meta: dict):
    required = ["id", "version", "name", "minAppVersion", "entryClass"]
    for field in required:
        if field not in meta:
            raise ValueError(f"plugin.json missing required field: {field}")
        if not isinstance(meta[field], str) or not meta[field].strip():
            raise ValueError(f"plugin.json '{field}' must be a non-empty string")
    if "/" in meta["id"]:
        raise ValueError("plugin.id must be a string without '/'")
    if meta.get("maxAppVersion") is not None and not isinstance(meta["maxAppVersion"], str):
        raise ValueError("plugin.maxAppVersion must be a string or null")


def extract_and_normalize_file(tar: tarfile.TarFile, tar_members: list[str], pattern: str, dest: Path) -> bool:
    """Finds a file inside the archive using case-insensitive matching and renames it on extraction."""
    # Find the first file inside the archive matching the lowercase target name
    matched_name = next((m for m in tar_members if m.lower() == pattern.lower()), None)
    
    if matched_name:
        try:
            f = tar.extractfile(matched_name)
            if f:
                dest.parent.mkdir(parents=True, exist_ok=True)
                with open(dest, "wb") as out:
                    out.write(f.read())
                return True
        except KeyError:
            pass
    return False


def update_index(plugin_id: str, meta: dict):
    index_path = PLUGINS_DIR / "index.json"
    if index_path.exists():
        with open(index_path) as f:
            index = json.load(f)
    else:
        index = []

    # Remove old entry for this ID
    index = [e for e in index if e["id"] != plugin_id]

    entry = {
        "id": plugin_id,
        "name": meta["name"],
        "version": meta["version"],
        "description": meta.get("description", ""),
        "author": meta.get("author", {}).get("name", ""),
        "minAppVersion": meta["minAppVersion"],
        "maxAppVersion": meta.get("maxAppVersion"),
    }
    index.append(entry)
    index.sort(key=lambda x: x["name"].lower())

    with open(index_path, "w") as f:
        json.dump(index, f, indent=2)
        f.write("\n")


def main():
    bundle_files = list(INCOMING_DIR.glob("*.klyx"))
    if not bundle_files:
        print("No .klyx files found in workspace", flush=True)
        return

    for bundle in bundle_files:
        print(f"Processing: {bundle.name}", flush=True)

        with tarfile.open(bundle, "r:gz") as tar:
            meta = extract_plugin_json(tar)
            validate_meta(meta)

            plugin_id = meta["id"]
            plugin_version = meta["version"]
            plugin_dir = PLUGINS_DIR / plugin_id

            # Cache the archive member list to prevent repeated disk-seek calculations
            tar_members = tar.getnames()

            # Save bundle
            plugin_dir.mkdir(parents=True, exist_ok=True)
            bundle_dest = plugin_dir / f"{plugin_version}.klyx"
            shutil.copy2(bundle, bundle_dest)

            # Extract metadata
            meta_path = plugin_dir / "metadata.json"
            with open(meta_path, "w") as f:
                json.dump(meta, f, indent=2)
                f.write("\n")

            supported_extensions = [".png", ".webp", ".jpg", ".jpeg"]
            for ext in supported_extensions:
                # Scans case-insensitively for icon.png, icon.PNG, Icon.WebP, etc.
                if extract_and_normalize_file(tar, tar_members, f"icon{ext}", plugin_dir / "icon.png"):
                    break

            extract_and_normalize_file(tar, tar_members, "readme.md", plugin_dir / "readme.md")
            extract_and_normalize_file(tar, tar_members, "changelog.md", plugin_dir / "changelog.md")

            owner = get_owner_for(plugin_id)
            if owner:
                owner_path = plugin_dir / ".owner"
                owner_path.write_text(owner + "\n")

            # Update index
            update_index(plugin_id, meta)

            print(f"Published: {plugin_id} v{plugin_version}", flush=True)

    for f in INCOMING_DIR.glob("*.klyx"):
        f.unlink()


if __name__ == "__main__":
    main()
