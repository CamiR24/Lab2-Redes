package models;

/**
 * Misma idea que el Frame del emisor: un único objeto que va evolucionando
 * a medida que pasa por cada capa. Cada capa del receptor solo lee/escribe
 * los campos que le corresponden.
 */
public class Frame {

    // Trama binaria cruda tal como llegó por el socket (Cabecera+Datos+Integridad)
    public String rawPayload = "";

    // Capa de Enlace
    public Algorithm algorithm = Algorithm.DESCONOCIDO;
    public String dataBits = "";        // datos ya separados de cabecera/integridad
    public String receivedIntegrity = ""; // integridad tal como llegó (posiblemente con ruido)
    public boolean corrupted = false;    // se detectó un error
    public boolean corrected = false;    // el error detectado se pudo corregir
    public String errorDetail = "";      // detalle para debug/reporte

    // Capa de Presentación / Aplicación
    public String message = "";

    @Override
    public String toString() {
        return "Frame{" +
                "algorithm=" + algorithm +
                ", corrupted=" + corrupted +
                ", corrected=" + corrected +
                ", message='" + message + '\'' +
                '}';
    }
}
