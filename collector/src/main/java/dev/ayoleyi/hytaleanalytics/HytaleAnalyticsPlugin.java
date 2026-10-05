package dev.ayoleyi.hytaleanalytics;

import com.hypixel.hytale.server.core.HytaleServer;
import com.hypixel.hytale.server.core.event.events.player.PlayerConnectEvent;
import com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent;
import com.hypixel.hytale.server.core.plugin.JavaPlugin;
import com.hypixel.hytale.server.core.plugin.JavaPluginInit;
import com.hypixel.hytale.server.core.universe.PlayerRef;
import com.hypixel.hytale.server.core.universe.Universe;
import com.hypixel.hytale.server.core.universe.world.World;

import java.io.IOException;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ScheduledFuture;
import java.util.concurrent.TimeUnit;

/**
 * Minimal, privacy-conscious analytics collector for a server the portfolio
 * owner controls.
 *
 * It intentionally does NOT read Hytale's internal telemetry backend and it
 * does NOT collect usernames, IP addresses, chat text, auth tokens, or raw
 * UUIDs.
 */
public final class HytaleAnalyticsPlugin extends JavaPlugin {
    private static final long HEARTBEAT_SECONDS = 60L;

    private AnalyticsWriter writer;
    private Pseudonymizer pseudonymizer;
    private ScheduledFuture<?> heartbeatTask;
    private String serverId;

    public HytaleAnalyticsPlugin(JavaPluginInit init) {
        super(init);
    }

    @Override
    protected void setup() {
        try {
            Path dataDir = getDataDirectory();
            this.serverId = readServerId();
            this.pseudonymizer = Pseudonymizer.loadOrCreate(dataDir.resolve("analytics-secret.key"));
            this.writer = new AnalyticsWriter(dataDir, serverId);

            getEventRegistry().register(PlayerConnectEvent.class, this::onPlayerConnect);
            getEventRegistry().register(PlayerDisconnectEvent.class, this::onPlayerDisconnect);
        } catch (IOException e) {
            throw new IllegalStateException("Unable to initialize Hytale analytics collector", e);
        }
    }

    @Override
    protected void start() {
        heartbeatTask = HytaleServer.SCHEDULED_EXECUTOR.scheduleAtFixedRate(
            this::safeWriteHeartbeat,
            5L,
            HEARTBEAT_SECONDS,
            TimeUnit.SECONDS
        );
    }

    @Override
    protected void shutdown() {
        if (heartbeatTask != null) {
            heartbeatTask.cancel(false);
        }
        if (writer != null) {
            try {
                writer.close();
            } catch (IOException ignored) {
                // Server is already shutting down; do not block shutdown on analytics IO.
            }
        }
    }

    private void onPlayerConnect(PlayerConnectEvent event) {
        PlayerRef playerRef = event.getPlayerRef();
        String playerId = pseudonymizer.playerId(playerRef.getUuid());
        String worldName = event.getWorld() == null ? null : event.getWorld().getName();
        try {
            writer.writePlayerEvent("player_connect", playerId, worldName, null);
        } catch (Throwable ignored) {
            // A failed analytics write must never interrupt player connection handling.
        }
    }

    private void onPlayerDisconnect(PlayerDisconnectEvent event) {
        PlayerRef playerRef = event.getPlayerRef();
        String playerId = pseudonymizer.playerId(playerRef.getUuid());
        String worldName = resolveWorldName(playerRef.getWorldUuid());
        String reason = event.getDisconnectReason() == null
            ? null
            : event.getDisconnectReason().toString();
        try {
            writer.writePlayerEvent("player_disconnect", playerId, worldName, reason);
        } catch (Throwable ignored) {
            // A failed analytics write must never interrupt player disconnect handling.
        }
    }

    private void safeWriteHeartbeat() {
        try {
            writeHeartbeat();
        } catch (Throwable ignored) {
            // Analytics must never be able to crash the game server.
        }
    }

    private void writeHeartbeat() throws IOException {
        Universe universe = Universe.get();
        int playersOnline = universe == null ? 0 : universe.getPlayerCount();
        int worldCount = universe == null ? 0 : universe.getWorlds().size();

        Runtime runtime = Runtime.getRuntime();
        long usedBytes = runtime.totalMemory() - runtime.freeMemory();
        long maxBytes = runtime.maxMemory();
        long memoryUsedMb = usedBytes / (1024L * 1024L);
        long memoryMaxMb = maxBytes / (1024L * 1024L);

        List<AnalyticsWriter.WorldHeartbeat> worlds = new ArrayList<>();
        if (universe != null) {
            for (Map.Entry<String, World> entry : universe.getWorlds().entrySet()) {
                World world = entry.getValue();
                worlds.add(new AnalyticsWriter.WorldHeartbeat(
                    world.getName(),
                    world.getPlayerCount(),
                    world.getTps(),
                    readAverageTickMs(world)
                ));
            }
        }

        writer.writeHeartbeat(playersOnline, worldCount, memoryUsedMb, memoryMaxMb, worlds);
    }

    private static Double readAverageTickMs(World world) {
        try {
            long[] values = world.getBufferedTickLengthMetricSet().getAllValues();
            if (values == null || values.length == 0) {
                return null;
            }
            long sum = 0L;
            int count = 0;
            for (long value : values) {
                if (value > 0) {
                    sum += value;
                    count++;
                }
            }
            if (count == 0) {
                return null;
            }
            // TickingThread's historic tick-length metric is represented in nanoseconds.
            return (sum / (double) count) / 1_000_000.0;
        } catch (Throwable ignored) {
            return null;
        }
    }

    private static String resolveWorldName(UUID worldUuid) {
        if (worldUuid == null) return null;
        try {
            Universe universe = Universe.get();
            if (universe == null) return null;
            World world = universe.getWorld(worldUuid);
            return world == null ? null : world.getName();
        } catch (Throwable ignored) {
            return null;
        }
    }

    private static String readServerId() {
        String configured = System.getenv("HYTALE_ANALYTICS_SERVER_ID");
        if (configured == null || configured.isBlank()) {
            return "local-hytale-server";
        }
        return configured.trim();
    }
}
