package link.algorithms;

/**
 * Verificación y corrección de errores con Hamming (algoritmo de
 * CORRECCIÓN), simétrico a Emisor/link/algorithms/algoritmo2.py.
 *
 * Mismo esquema sistemático generalizado: r = mínimo de bits de paridad tal
 * que (m + r + 1) <= 2^r, transmitidos al final de los m bits de datos.
 * Cada bit de dato se asocia a la posición que ocuparía en un Hamming
 * clásico (intercalado) para saber en qué ecuaciones de paridad participa.
 *
 * El receptor solo conoce L = m + r (longitud total tras quitar la
 * cabecera), no m ni r por separado. Pero como el emisor siempre usa el
 * mínimo r que satisface (m + r + 1) <= 2^r, y L = m + r, esa condición es
 * equivalente a 2^r >= L + 1. Por lo tanto basta con encontrar el mínimo r
 * tal que 2^r >= L + 1 para reconstruir el mismo r usado por el emisor
 * (queda demostrado que ambas condiciones son equivalentes).
 */
public class Hamming {

    public int requiredParityBitsFromTotalLength(int totalLength) {
        int r = 1;
        while ((1L << r) < (totalLength + 1)) {
            r++;
        }
        return r;
    }

    /** Calcula los bits de paridad de una cadena de datos, dado un número de bits de paridad r. */
    public String calculateParity(String dataBits, int r) {
        int[] parity = new int[r];

        for (int dataIndex = 0; dataIndex < dataBits.length(); dataIndex++) {
            if (dataBits.charAt(dataIndex) == '0') {
                continue;
            }
            int virtualPosition = virtualPosition(dataIndex);
            for (int k = 0; k < r; k++) {
                if (((virtualPosition >> k) & 1) != 0) {
                    parity[k] ^= 1;
                }
            }
        }

        StringBuilder result = new StringBuilder();
        for (int k = r - 1; k >= 0; k--) {
            result.append(parity[k]);
        }
        return result.toString();
    }

    /** Resultado de verificar/corregir un bloque Hamming. */
    public static class Result {
        public boolean corrupted;
        public boolean corrected;
        public String data;
        public String detail;
    }

    public Result verifyAndCorrect(String data, String receivedParity) {
        Result result = new Result();
        int r = receivedParity.length();

        String recalculatedParity = calculateParity(data, r);
        int syndrome = Integer.parseInt(receivedParity, 2) ^ Integer.parseInt(recalculatedParity, 2);

        if (syndrome == 0) {
            result.corrupted = false;
            result.corrected = false;
            result.data = data;
            result.detail = "Sin errores detectados.";
            return result;
        }

        result.corrupted = true;

        if (isPowerOfTwo(syndrome)) {
            // El error está en un bit de paridad; los datos siguen intactos.
            result.corrected = true;
            result.data = data;
            result.detail = "Error detectado en un bit de paridad (posición " + syndrome + "); los datos no se vieron afectados.";
            return result;
        }

        int dataIndex = virtualPositionToDataIndex(syndrome, data.length());

        if (dataIndex < 0) {
            // El síndrome no corresponde a ningún bit de dato válido:
            // hay más de un bit con error y el código de Hamming (SEC)
            // no puede corregirlo de forma confiable.
            result.corrected = false;
            result.data = data;
            result.detail = "Error detectado pero no corregible (probablemente más de 1 bit alterado).";
            return result;
        }

        char[] corrected = data.toCharArray();
        corrected[dataIndex] = corrected[dataIndex] == '0' ? '1' : '0';

        result.corrected = true;
        result.data = new String(corrected);
        result.detail = "Error de 1 bit corregido en la posición de datos " + dataIndex + ".";
        return result;
    }

    private boolean isPowerOfTwo(int value) {
        return (value & (value - 1)) == 0;
    }

    /**
     * Traduce el índice de un bit de dato (0-based) a la posición (1-based)
     * que ocuparía en un Hamming clásico intercalado, saltando las
     * posiciones que son potencia de 2 (reservadas para paridad).
     */
    private int virtualPosition(int dataIndex) {
        int position = 1;
        int dataSeen = 0;

        while (true) {
            boolean isPowerOfTwo = (position & (position - 1)) == 0;
            if (!isPowerOfTwo) {
                if (dataSeen == dataIndex) {
                    return position;
                }
                dataSeen++;
            }
            position++;
        }
    }

    /** Inverso de virtualPosition: dado un síndrome (posición virtual), devuelve el índice de dato, o -1 si está fuera de rango. */
    private int virtualPositionToDataIndex(int virtualPosition, int dataLength) {
        int position = 1;
        int dataIndex = 0;

        while (dataIndex < dataLength) {
            boolean isPowerOfTwo = (position & (position - 1)) == 0;
            if (!isPowerOfTwo) {
                if (position == virtualPosition) {
                    return dataIndex;
                }
                dataIndex++;
            }
            position++;
        }
        return -1;
    }
}
