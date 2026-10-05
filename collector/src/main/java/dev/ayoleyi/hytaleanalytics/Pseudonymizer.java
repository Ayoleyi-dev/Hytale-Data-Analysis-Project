package dev.ayoleyi.hytaleanalytics;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.GeneralSecurityException;
import java.security.SecureRandom;
import java.util.Base64;
import java.util.HexFormat;
import java.util.UUID;

/**
 * Stable HMAC-based pseudonymization for player UUIDs.
 *
 * Raw UUIDs are never written to analytics output. The secret remains in the
 * plugin data directory and should not be committed to source control.
 */
final class Pseudonymizer {
    private static final String ALGORITHM = "HmacSHA256";
    private static final int SECRET_BYTES = 32;
    private static final int OUTPUT_BYTES = 16;

    private final byte[] secret;

    private Pseudonymizer(byte[] secret) {
        this.secret = secret.clone();
    }

    static Pseudonymizer loadOrCreate(Path secretFile) throws IOException {
        byte[] secret;
        if (Files.exists(secretFile)) {
            String encoded = Files.readString(secretFile, StandardCharsets.UTF_8).trim();
            secret = Base64.getDecoder().decode(encoded);
            if (secret.length < 16) {
                throw new IOException("Analytics pseudonymization secret is unexpectedly short");
            }
        } else {
            secret = new byte[SECRET_BYTES];
            new SecureRandom().nextBytes(secret);
            Files.createDirectories(secretFile.getParent());
            Files.writeString(
                secretFile,
                Base64.getEncoder().encodeToString(secret),
                StandardCharsets.UTF_8
            );
        }
        return new Pseudonymizer(secret);
    }

    String playerId(UUID uuid) {
        try {
            Mac mac = Mac.getInstance(ALGORITHM);
            mac.init(new SecretKeySpec(secret, ALGORITHM));
            byte[] digest = mac.doFinal(uuid.toString().getBytes(StandardCharsets.UTF_8));
            byte[] shortened = new byte[OUTPUT_BYTES];
            System.arraycopy(digest, 0, shortened, 0, OUTPUT_BYTES);
            return "p_" + HexFormat.of().formatHex(shortened);
        } catch (GeneralSecurityException e) {
            throw new IllegalStateException("Unable to pseudonymize player UUID", e);
        }
    }
}
