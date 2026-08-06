package presentation;

import models.Frame;

/**
 * Capa de Presentación del receptor: decodifica ASCII binario a texto.
 * Espejo de Emisor/presentation/presentation_layer.py.
 */
public class PresentationLayer {

    public Frame decode(Frame frame) {
        // Si quedó un error sin corregir, no tiene sentido decodificar.
        if (frame.corrupted && !frame.corrected) {
            frame.message = null;
            return frame;
        }

        String bits = frame.dataBits;

        if (bits.length() % 8 != 0) {
            // Datos corruptos/mal alineados: no se puede decodificar de forma confiable.
            frame.corrupted = true;
            frame.corrected = false;
            frame.message = null;
            return frame;
        }

        StringBuilder message = new StringBuilder();
        for (int i = 0; i < bits.length(); i += 8) {
            String byteStr = bits.substring(i, i + 8);
            int codePoint = Integer.parseInt(byteStr, 2);
            message.append((char) codePoint);
        }

        frame.message = message.toString();
        return frame;
    }
}
