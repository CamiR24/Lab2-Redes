import application.ApplicationLayer;
import application.ReceptorWindow;
import link.LinkLayer;
import models.Frame;
import presentation.PresentationLayer;
import transport.SocketServer;

import javax.swing.*;

public class Main {

    public static void main(String[] args) {
        LinkLayer link = new LinkLayer();
        PresentationLayer presentation = new PresentationLayer();
        ApplicationLayer application = new ApplicationLayer();

        SwingUtilities.invokeLater(() -> {
            ReceptorWindow window = new ReceptorWindow();

            window.setOnStart(port -> {
                SocketServer server = new SocketServer(port);

                Thread serverThread = new Thread(() -> server.listen(
                        rawPayload -> {
                            Frame frame = new Frame();
                            frame.rawPayload = rawPayload;

                            Frame processed = link.verifyIntegrity(frame);
                            processed = presentation.decode(processed);
                            application.showMessage(processed);

                            Frame finalFrame = processed;
                            SwingUtilities.invokeLater(() -> window.showFrame(finalFrame));
                        },
                        new SocketServer.StatusListener() {
                            @Override
                            public void onListening(int listeningPort) {
                                SwingUtilities.invokeLater(() -> window.showListening(listeningPort));
                            }

                            @Override
                            public void onError(String message) {
                                SwingUtilities.invokeLater(() -> window.showError(message));
                            }
                        }
                ));

                serverThread.setDaemon(true);
                serverThread.start();
            });

            window.setVisible(true);
        });
    }
}