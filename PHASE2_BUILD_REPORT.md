# Phase 2 Build Report

## Completed

- Added a Java Hytale server-side collector.
- Added HMAC player pseudonymization.
- Added append-only JSONL event and heartbeat output.
- Added player connect/disconnect collection.
- Added limited local server/world health collection.
- Added Python observed-data ingestion and validation.
- Added deterministic connect→disconnect session reconstruction.
- Added a dedicated observed-data dashboard page.
- Added a data provenance page.
- Added test fixtures for observed collector output.
- Added three collector-specific automated tests.
- Added Git exclusions for observed JSONL, generated output, build artifacts and the
  HMAC secret.

## Validation performed in the build workspace

- Python test suite: 6 tests passed.
- Python source: bytecode compilation passed.
- Fixture ingestion: completed with 2 reconstructed sessions and all quality checks
  passing.
- Java helper classes: compiled successfully in the available JDK.
- Full Java plugin source: syntax/API-shape compiled against local stubs matching the
  public API methods used.

## Validation that still requires the Hytale installation

The build workspace does not contain the user's licensed/current HytaleServer.jar or
Java 25 runtime, so one validation step is deliberately not claimed as complete:

- compile `collector/` against the exact installed HytaleServer.jar using Java 25;
- place the built JAR in `mods/`;
- launch a development server;
- observe a real connect/disconnect pair and at least several heartbeats;
- ingest those JSONL files and confirm the Observed Server Data page.

This is the correct final compatibility test because Hytale's plugin/API surface is
still changing during Early Access.
