package link;

import link.algorithms.CRC32Check;
import link.algorithms.Hamming;
import models.Algorithm;
import models.Frame;

/**
 * Capa de Enlace del receptor: separa cabecera/datos/integridad, verifica
 * integridad con el algoritmo indicado por la cabecera y, si el algoritmo
 * lo permite (Hamming), corrige el mensaje. Espejo de Emisor/link/link_layer.py.
 */
public class LinkLayer {

    private static final int HEADER_LENGTH = 8;

    private final CRC32Check crc32 = new CRC32Check();
    private final Hamming hamming = new Hamming();

    public Frame verifyIntegrity(Frame frame) {
        if (frame.rawPayload.length() < HEADER_LENGTH) {
            frame.algorithm = Algorithm.DESCONOCIDO;
            frame.corrupted = true;
            frame.errorDetail = "Trama demasiado corta para contener una cabecera.";
            return frame;
        }

        String header = frame.rawPayload.substring(0, HEADER_LENGTH);
        String rest = frame.rawPayload.substring(HEADER_LENGTH);
        frame.algorithm = Algorithm.fromHeader(header);

        switch (frame.algorithm) {
            case CRC32:
                return verifyCrc32(frame, rest);
            case HAMMING:
                return verifyHamming(frame, rest);
            default:
                frame.corrupted = true;
                frame.errorDetail = "Cabecera desconocida ('" + header + "'); no se puede interpretar el algoritmo " +
                        "(posiblemente el ruido alteró la cabecera).";
                return frame;
        }
    }

    private Frame verifyCrc32(Frame frame, String rest) {
        int integrityLength = crc32.integrityLength();

        if (rest.length() <= integrityLength) {
            frame.corrupted = true;
            frame.errorDetail = "Trama demasiado corta para CRC32.";
            return frame;
        }

        String data = rest.substring(0, rest.length() - integrityLength);
        String receivedIntegrity = rest.substring(rest.length() - integrityLength);

        frame.dataBits = data;
        frame.receivedIntegrity = receivedIntegrity;

        if (data.length() % 8 != 0) {
            // Esto puede pasar si el ruido corrompió la cabecera y una trama
            // de otro algoritmo se interpretó por error como CRC32.
            frame.corrupted = true;
            frame.corrected = false;
            frame.errorDetail = "Trama inválida para CRC32 (datos no alineados a bytes; " +
                    "probablemente el ruido corrompió la cabecera).";
            return frame;
        }

        String recalculated = crc32.calculate(data);

        if (recalculated.equals(receivedIntegrity)) {
            frame.corrupted = false;
            frame.corrected = false;
            frame.errorDetail = "CRC32 correcto, sin errores detectados.";
        } else {
            // CRC32 es un algoritmo de DETECCIÓN, no puede corregir.
            frame.corrupted = true;
            frame.corrected = false;
            frame.errorDetail = "CRC32 no coincide: se detectó un error, pero CRC32 no puede corregirlo.";
        }

        return frame;
    }

    private Frame verifyHamming(Frame frame, String rest) {
        int totalLength = rest.length();
        int r = hamming.requiredParityBitsFromTotalLength(totalLength);
        int m = totalLength - r;

        if (m < 0) {
            frame.corrupted = true;
            frame.errorDetail = "Trama demasiado corta para Hamming.";
            return frame;
        }

        String data = rest.substring(0, m);
        String receivedParity = rest.substring(m);
        frame.dataBits = data;
        frame.receivedIntegrity = receivedParity;

        Hamming.Result result = hamming.verifyAndCorrect(data, receivedParity);

        frame.corrupted = result.corrupted;
        frame.corrected = result.corrected;
        frame.dataBits = result.data;
        frame.errorDetail = result.detail;

        return frame;
    }
}