package models;

public enum Algorithm {
    CRC32("00000001"),
    HAMMING("00000010"),
    DESCONOCIDO("");

    private final String headerCode;

    Algorithm(String headerCode) {
        this.headerCode = headerCode;
    }

    public String headerCode() {
        return headerCode;
    }

    public static Algorithm fromHeader(String header) {
        for (Algorithm algorithm : values()) {
            if (algorithm.headerCode.equals(header)) {
                return algorithm;
            }
        }
        return DESCONOCIDO;
    }
}
