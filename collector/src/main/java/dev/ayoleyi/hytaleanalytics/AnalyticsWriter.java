package dev.ayoleyi.hytaleanalytics;

import java.io.BufferedWriter;
import java.io.Closeable;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.time.Instant;
import java.util.List;

final class AnalyticsWriter implements Closeable {
    static final int SCHEMA_VERSION = 1;

    record WorldHeartbeat(
        String worldName,
        int playersOnline,
        int configuredTps,
        Double averageTickMs
    ) {}

    private final BufferedWriter eventsWriter;
    private final BufferedWriter heartbeatWriter;
    private final String serverId;

    AnalyticsWriter(Path dataDirectory, String serverId) throws IOException {
        Path outputDir = dataDirectory.resolve("analytics");
        Files.createDirectories(outputDir);
        this.eventsWriter = Files.newBufferedWriter(
            outputDir.resolve("analytics-events.jsonl"),
            StandardCharsets.UTF_8,
            StandardOpenOption.CREATE,
            StandardOpenOption.WRITE,
            StandardOpenOption.APPEND
        );
        this.heartbeatWriter = Files.newBufferedWriter(
            outputDir.resolve("server-heartbeats.jsonl"),
            StandardCharsets.UTF_8,
            StandardOpenOption.CREATE,
            StandardOpenOption.WRITE,
            StandardOpenOption.APPEND
        );
        this.serverId = serverId;
    }

    synchronized void writePlayerEvent(
        String eventType,
        String playerId,
        String worldName,
        String disconnectReason
    ) throws IOException {
        String json = "{" +
            "\"schema_version\":" + SCHEMA_VERSION + "," +
            "\"observed_at\":" + JsonUtil.quote(Instant.now().toString()) + "," +
            "\"source\":\"hytale_server_plugin\"," +
            "\"server_id\":" + JsonUtil.quote(serverId) + "," +
            "\"event_type\":" + JsonUtil.quote(eventType) + "," +
            "\"player_id\":" + JsonUtil.quote(playerId) + "," +
            "\"world_name\":" + JsonUtil.quote(worldName) + "," +
            "\"disconnect_reason\":" + JsonUtil.quote(disconnectReason) +
            "}";
        eventsWriter.write(json);
        eventsWriter.newLine();
        eventsWriter.flush();
    }

    synchronized void writeHeartbeat(
        int playersOnline,
        int worldCount,
        long memoryUsedMb,
        long memoryMaxMb,
        List<WorldHeartbeat> worlds
    ) throws IOException {
        StringBuilder worldJson = new StringBuilder("[");
        for (int i = 0; i < worlds.size(); i++) {
            if (i > 0) worldJson.append(',');
            WorldHeartbeat world = worlds.get(i);
            worldJson.append('{')
                .append("\"world_name\":").append(JsonUtil.quote(world.worldName())).append(',')
                .append("\"players_online\":").append(world.playersOnline()).append(',')
                .append("\"configured_tps\":").append(world.configuredTps()).append(',')
                .append("\"average_tick_ms\":")
                .append(world.averageTickMs() == null ? "null" : String.format(java.util.Locale.ROOT, "%.4f", world.averageTickMs()))
                .append('}');
        }
        worldJson.append(']');

        String json = "{" +
            "\"schema_version\":" + SCHEMA_VERSION + "," +
            "\"observed_at\":" + JsonUtil.quote(Instant.now().toString()) + "," +
            "\"source\":\"hytale_server_plugin\"," +
            "\"server_id\":" + JsonUtil.quote(serverId) + "," +
            "\"event_type\":\"server_heartbeat\"," +
            "\"players_online\":" + playersOnline + "," +
            "\"world_count\":" + worldCount + "," +
            "\"memory_used_mb\":" + memoryUsedMb + "," +
            "\"memory_max_mb\":" + memoryMaxMb + "," +
            "\"worlds\":" + worldJson +
            "}";
        heartbeatWriter.write(json);
        heartbeatWriter.newLine();
        heartbeatWriter.flush();
    }

    @Override
    public synchronized void close() throws IOException {
        eventsWriter.close();
        heartbeatWriter.close();
    }
}
