import application.ApplicationLayer;
import link.LinkLayer;
import models.Frame;
import presentation.PresentationLayer;
import transport.SocketServer;

import java.util.Scanner;

public class Main {

    public static void main(String[] args) {
        int port = readPort(args);

        LinkLayer link = new LinkLayer();
        PresentationLayer presentation = new PresentationLayer();
        ApplicationLayer application = new ApplicationLayer();

        SocketServer server = new SocketServer(port);

        server.listen(rawPayload -> {
            Frame frame = new Frame();
            frame.rawPayload = rawPayload;

            frame = link.verifyIntegrity(frame);
            System.out.println("\n========== LINK ==========");
            System.out.println("Algoritmo detectado : " + frame.algorithm);
            System.out.println("Datos               : " + frame.dataBits);
            System.out.println("Integridad recibida : " + frame.receivedIntegrity);

            frame = presentation.decode(frame);
            System.out.println("\n========== PRESENTATION ==========");
            System.out.println(frame.corrupted && !frame.corrected ? "(no decodificable)" : frame.message);

            application.showMessage(frame);
        });
    }

    private static int readPort(String[] args) {
        if (args.length > 0) {
            try {
                return Integer.parseInt(args[0]);
            } catch (NumberFormatException ignored) {
                // sigue al modo interactivo
            }
        }

        Scanner scanner = new Scanner(System.in);
        System.out.print("Puerto en el que escuchará el receptor: ");
        while (!scanner.hasNextInt()) {
            System.out.print("Ingrese un puerto válido: ");
            scanner.next();
        }
        return scanner.nextInt();
    }
}
