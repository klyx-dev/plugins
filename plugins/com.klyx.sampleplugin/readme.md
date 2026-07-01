# Klyx Sample Plugin

A reference implementation showing the Klyx plugin API capabilities.

## Features

- Registers a toolbar action ("Sample Greeting") in the overflow menu
- Registers a custom settings screen with a greeting message
- Demonstrates plugin lifecycle (onPluginLoad / onPluginUnload)

## Building

```bash
./gradlew klyxBundle
# Output: build/klyx/SamplePlugin.klyx
```
