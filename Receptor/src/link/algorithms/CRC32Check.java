package link.algorithms;

import java.util.zip.CRC32;

/**
 * Verificación de integridad con CRC32 (algoritmo de DETECCIÓN, no corrige).
 *
 * Usa java.util.zip.CRC32, que implementa el mismo algoritmo que zlib.crc32
 * en Python (polinomio reflejado 0xEDB88320, valor inicial 0xFFFFFFFF, XOR
 * final 0xFFFFFFFF) contra el cual ya está probado el emisor
 * (Emisor/tests/test_crc32.py), así que ambos lados quedan compatibles.
 */
public class CRC32Check {

    private static final int INTEGRITY_LENGTH = 32;

    public int integrityLength() {
        return INTEGRITY_LENGTH;
    }

    /** Calcula el CRC32 de una cadena de bits (debe estar alineada a bytes) y lo devuelve como cadena de 32 bits. */
    public String calculate(String dataBits) {
        if (dataBits.length() % 8 != 0) {
            throw new IllegalArgumentException("El mensaje binario debe estar alineado a bytes.");
        }

        byte[] data = toBytes(dataBits);

        CRC32 crc32 = new CRC32();
        crc32.update(data);

        long value = crc32.getValue(); // 32 bits sin signo
        return toBinaryString(value, INTEGRITY_LENGTH);
    }

    private byte[] toBytes(String dataBits) {
        int byteCount = dataBits.length() / 8;
        byte[] bytes = new byte[byteCount];
        for (int i = 0; i < byteCount; i++) {
            String byteStr = dataBits.substring(i * 8, i * 8 + 8);
            bytes[i] = (byte) Integer.parseInt(byteStr, 2);
        }
        return bytes;
    }

    private String toBinaryString(long value, int length) {
        String binary = Long.toBinaryString(value);
        StringBuilder padded = new StringBuilder();
        for (int i = binary.length(); i < length; i++) {
            padded.append('0');
        }
        padded.append(binary);
        return padded.toString();
    }
}
