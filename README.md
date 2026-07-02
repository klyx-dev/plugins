# Klyx Plugin Registry

Community plugin registry for [Klyx](https://klyx-dev.github.io). This repository hosts and validates community-built Klyx plugins distributed as `.klyx` bundle files.

## For Plugin Authors

### Prerequisites

1. A `plugin.json` at the root of your project (see [sample]())
2. The `io.github.klyx-dev.plugin` Gradle plugin applied

### Build

```bash
./gradlew klyxBundle
```

The default output goes in `app/build/klyx/my-plugin.klyx`.

### Publish

**Via GitHub PR:**
1. [Fork](https://github.com/klyx-dev/plugins/fork) the registry repo
2. Add your `.klyx` file to the `incoming/` directory
3. Create a pull request
4. CI validates the bundle; wait for merge

### Bundle Format

A `.klyx` file is a gzipped tarball containing:

| Entry | Required | Description |
|-------|----------|-------------|
| `plugin.json` | Yes | Plugin metadata (id, version, name, etc.) |
| `plugin.apk` | Yes | The compiled APK |
| `icon.png` | No | Store icon (512x512 recommended) |
| `readme.md` | No | Plugin description / docs |
| `changelog.md` | No | Version changelog |

## Repository Structure

```
plugins/
  index.json        <- Auto-generated registry
  {plugin-id}/
    metadata.json   <- Extracted plugin.json
    icon.png        <- Extracted plugin icon
    readme.md       <- Extracted readme
    changelog.md    <- Extracted changelog
    {version}.klyx  <- Bundle files
incoming/           <- Drop .klyx files here (via PR)
```

---

## Contributing

See the [publishing guide](#publish) above. All submissions are validated by CI before merging.
