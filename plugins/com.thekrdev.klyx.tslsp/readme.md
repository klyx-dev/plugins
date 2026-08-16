# TypeScript Lsp

JavaScript and TypeScript language server provider for [Klyx](https://github.com/klyx-dev/klyx).

## Building

Clone the repo
```
git clone https://github.com/thekrdev/klyx-typescript-lsp.git
```

The Klyx Gradle Plugin registers the following tasks in the `klyx` group:

- `klyxBundleDebug`: Packages the debug APK into a `.klyx` archive.
- `klyxBundleRelease`: Packages the release APK into a `.klyx` archive.
- `klyxBundle`: Alias for `klyxBundleRelease`.

Run the default task:

```
./gradlew klyxBundle
```

Output: `output/TypeScript LSP.klyx`

## License

MIT