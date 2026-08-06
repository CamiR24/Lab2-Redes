package application;

import models.Frame;

/**
 * Capa de Aplicación del receptor: muestra el mensaje final al usuario,
 * o un mensaje de error si se detectaron errores que no se pudieron corregir.
 * Espejo de Emisor/application/application_layer.py (servicio mostrar_mensaje).
 */
public class ApplicationLayer {

    public void showMessage(Frame frame) {
        System.out.println("\n========== APPLICATION ==========");
        System.out.println("Algoritmo utilizado : " + frame.algorithm);
        System.out.println("Detalle             : " + frame.errorDetail);

        if (frame.corrupted && !frame.corrected) {
            System.out.println("\n*** ERROR: se detectaron errores en la trama y no fue posible corregirlos. ***");
            return;
        }

        if (frame.corrupted && frame.corrected) {
            System.out.println("(Se detectó un error y fue corregido automáticamente.)");
        }

        System.out.println("\nMensaje recibido: " + frame.message);
    }
}
