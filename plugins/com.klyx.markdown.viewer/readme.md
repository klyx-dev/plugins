# Markdown Viewer

A plugin for [Klyx](https://github.com/klyx-dev/klyx) that can run markdown files as preview inside the app.

## Features

- Opens `.md` and `.markdown` files in a dedicated preview screen.
- Registers a file runner, so markdown files open automatically from the file tree.
- Syntax-highlighted code blocks with header/fence support.

## Building

The Klyx Gradle Plugin registers the following tasks in the `klyx` group:

- `klyxBundleDebug`: Packages the debug APK into a `.klyx` archive.
- `klyxBundleRelease`: Packages the release APK into a `.klyx` archive.
- `klyxBundle`: Alias for `klyxBundleRelease`.

Run the default task:

```
./gradlew klyxBundle
```

Output: `output/MarkdownViewerPlugin.klyx`

## Bundle Contents

The generated `.klyx` archive contains:

- `plugin.apk`: The plugin APK (debug or release variant).
- `plugin.json`: The plugin descriptor with id, name, version, entryClass, author, and links.
- `icon.png`: The plugin icon.
- `readme.md`: This file.

## License

MIT
