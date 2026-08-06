package transport;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.charset.StandardCharsets;

/**
 * Capa de Transmisión del receptor: escucha en un puerto y recibe la trama
 * binaria (como texto de '0'/'1', igual que el emisor la envía). Espejo de
 * Emisor/transport/socket_client.py, pero del lado que recibe.
 *
 * El receptor siempre queda escuchando: tras procesar un mensaje, vuelve a
 * aceptar la siguiente conexión.
 */
public class SocketServer {

    private final int port;

    public SocketServer(int port) {
        this.port = port;
    }

    public interface FrameHandler {
        void handle(String rawPayload);
    }

    public void listen(FrameHandler handler) {
        try (ServerSocket serverSocket = new ServerSocket(port)) {
            System.out.println("Receptor escuchando en el puerto " + port + "...");

            while (true) {
                try (Socket client = serverSocket.accept()) {
                    String payload = readAll(client.getInputStream());
                    System.out.println("\n========== TRANSMISSION ==========");
                    System.out.println("Trama recibida (" + payload.length() + " bits).");
                    handler.handle(payload);
                } catch (IOException error) {
                    System.out.println("Error al recibir la trama: " + error.getMessage());
                }
                System.out.println("\nEsperando la siguiente trama...");
            }
        } catch (IOException error) {
            System.out.println("No fue posible iniciar el receptor en el puerto " + port + ": " + error.getMessage());
        }
    }

    private String readAll(InputStream inputStream) throws IOException {
        ByteArrayOutputStream buffer = new ByteArrayOutputStream();
        byte[] chunk = new byte[4096];
        int bytesRead;
        while ((bytesRead = inputStream.read(chunk)) != -1) {
            buffer.write(chunk, 0, bytesRead);
        }
        return buffer.toString(StandardCharsets.UTF_8);
    }
}
