#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${HYTALE_SERVER_JAR:-}" ]]; then
  echo "ERROR: HYTALE_SERVER_JAR is not set."
  echo "Example: export HYTALE_SERVER_JAR=/path/to/HytaleServer.jar"
  exit 1
fi

if [[ ! -f "$HYTALE_SERVER_JAR" ]]; then
  echo "ERROR: HytaleServer.jar not found at $HYTALE_SERVER_JAR"
  exit 1
fi

rm -rf build
mkdir -p build/classes
find src/main/java -name '*.java' > build/sources.txt
javac --release 25 -cp "$HYTALE_SERVER_JAR" -d build/classes @build/sources.txt
cp src/main/resources/manifest.json build/classes/manifest.json
jar --create --file build/HytaleAnalyticsCollector-0.2.0.jar -C build/classes .
echo "Built: build/HytaleAnalyticsCollector-0.2.0.jar"
