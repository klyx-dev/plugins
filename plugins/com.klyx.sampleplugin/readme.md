# Klyx Sample Plugin

A reference implementation that demonstrates every feature of the Klyx Plugin API (klyx-api).

## Build Tasks

The Klyx Gradle Plugin registers the following tasks in the `klyx` group:

- `klyxBundleDebug`: Packages the debug APK into a `.klyx` archive.
- `klyxBundleRelease`: Packages the release APK into a `.klyx` archive.
- `klyxBundle`: Alias for `klyxBundleRelease`.

Run the default task:

```
./gradlew klyxBundle
```

Output: `output/SamplePlugin.klyx`

## Bundle Contents

The generated `.klyx` archive contains:

- `plugin.apk`: The plugin APK (debug or release variant).
- `plugin.json`: The plugin descriptor with id, name, version, entryClass, author, links, and permissions.
- `icon.png`: The plugin icon.
- `readme.md`: This file.
- `changelog.md`: Version history.
- Extra files configured via `klyx.extraFiles` (if any).

## Gradle Plugin Configuration

The `app/build.gradle.kts` file contains detailed comments explaining every property of the `klyx` extension and every task. Key configuration handled automatically by the plugin:

- Applies `org.jetbrains.kotlin.plugin.serialization`
- Sets `minSdk = 28` and Java 21 compatibility
- Auto-detects `readme.md`, `changelog.md`, and `icon.png` / `icon.jpg` from the project root
- `enableCompose()` enables Jetpack Compose and sets `buildFeatures.compose = true`

## plugin.json

The plugin descriptor uses all available fields:

- id, name, version, minAppVersion, maxAppVersion, entryClass, description
- author with name, email, url, github
- links with source, issues, website, donate
- permissions list
