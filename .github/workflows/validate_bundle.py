#!/usr/bin/env python3
"""Validate a single .klyx bundle and report all issues found."""

import json
import re
import sys
import tarfile


def check_plugin_json(path: str) -> tuple[dict | None, list[str]]:
    errors = []
    try:
        with tarfile.open(path, "r:gz") as tar:
            members = tar.getnames()
            if "plugin.json" not in members:
                errors.append(f"Missing plugin.json in bundle")
                return None, errors
            f = tar.extractfile("plugin.json")
            if f is None:
                errors.append(f"Could not extract plugin.json")
                return None, errors
            try:
                meta = json.loads(f.read())
            except json.JSONDecodeError as e:
                errors.append(f"plugin.json has invalid JSON: {e}")
                return None, errors
    except tarfile.ReadError:
        errors.append(f"Not a valid .tar.gz archive")
        return None, errors
    except Exception as e:
        errors.append(f"Cannot read bundle: {e}")
        return None, errors
    return meta, errors


def validate_meta(path: str, meta: dict) -> list[str]:
    errors = []

    required_fields = [
        ("id", "string"),
        ("version", "string"),
        ("name", "string"),
        ("minAppVersion", "string"),
        ("entryClass", "string"),
    ]
    for field, expected_type in required_fields:
        if field not in meta:
            errors.append(f"plugin.json missing required field '{field}'")
        elif not isinstance(meta[field], str):
            errors.append(f"plugin.json '{field}' must be a string, got {type(meta[field]).__name__}")
        elif not meta[field].strip():
            errors.append(f"plugin.json '{field}' must not be empty")

    if "id" in meta and isinstance(meta["id"], str):
        if "/" in meta["id"]:
            errors.append("plugin.id must not contain '/'")
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9.]*$', meta["id"]):
            errors.append("plugin.id must start with a letter and contain only letters, digits, and dots")

    if "version" in meta and isinstance(meta["version"], str) and meta["version"].strip():
        if not re.match(r'^\d+\.\d+\.\d+', meta["version"]):
            errors.append(f"plugin.version '{meta['version']}' should follow semver (e.g. 1.0.0)")

    if "minAppVersion" in meta and isinstance(meta["minAppVersion"], str) and meta["minAppVersion"].strip():
        if not re.match(r'^\d+\.\d+\.\d+', meta["minAppVersion"]):
            errors.append(f"plugin.minAppVersion '{meta['minAppVersion']}' should follow semver (e.g. 4.2.0)")

    if "maxAppVersion" in meta and meta["maxAppVersion"] is not None:
        if not isinstance(meta["maxAppVersion"], str):
            errors.append("plugin.maxAppVersion must be a string or null")
        elif not re.match(r'^\d+\.\d+\.\d+', meta["maxAppVersion"]):
            errors.append(f"plugin.maxAppVersion '{meta['maxAppVersion']}' should follow semver (e.g. 5.0.0)")

    if "author" in meta:
        author = meta["author"]
        if isinstance(author, dict):
            if "name" not in author:
                errors.append("plugin.json 'author' object must have a 'name' field")
            elif not isinstance(author["name"], str) or not author["name"].strip():
                errors.append("plugin.json 'author.name' must be a non-empty string")
        elif not isinstance(author, str):
            errors.append("plugin.json 'author' must be a string or object")

    if "description" in meta and not isinstance(meta["description"], str):
        errors.append("plugin.json 'description' must be a string")

    if "entryClass" in meta and isinstance(meta["entryClass"], str) and meta["entryClass"].strip():
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_.]*$', meta["entryClass"]):
            errors.append(f"plugin.entryClass '{meta['entryClass']}' is not a valid fully-qualified class name")

    invalid_top_level = [k for k in meta if not k.isidentifier()]
    if invalid_top_level:
        errors.append(f"plugin.json contains invalid field names: {invalid_top_level}")

    return errors


def main():
    path = sys.argv[1]
    all_errors = []

    meta, json_errors = check_plugin_json(path)
    all_errors.extend(json_errors)

    if meta is not None:
        all_errors.extend(validate_meta(path, meta))

    if all_errors:
        for err in all_errors:
            print(f"❌ {path}: {err}", flush=True)
        sys.exit(1)

    print(f"✅ {path}: {meta['id']} v{meta['version']} valid", flush=True)


if __name__ == "__main__":
    main()
