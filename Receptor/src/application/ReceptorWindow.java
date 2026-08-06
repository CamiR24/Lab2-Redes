package application;

import models.Frame;

import javax.swing.*;
import javax.swing.border.EmptyBorder;
import javax.swing.border.LineBorder;
import java.awt.*;
import java.text.SimpleDateFormat;
import java.util.Date;

/**
 * Interfaz gráfica del receptor. Muestra en vivo lo que va pasando en cada
 * capa (Transmisión / Enlace / Presentación / Aplicación) por cada trama
 * recibida. Sigue la misma paleta de colores que la ventana del Emisor
 * (application/main_window.py) para que ambas se vean consistentes.
 */
public class ReceptorWindow extends JFrame {

    private static final Color BACKGROUND = Color.decode("#FFFDF8");
    private static final Color TEXT = Color.decode("#334155");
    private static final Color TITLE_COLOR = Color.decode("#EC4899");
    private static final Color BORDER_COLOR = Color.decode("#7DD3FC");
    private static final Color BUTTON_COLOR = Color.decode("#F472B6");
    private static final Color BUTTON_HOVER = Color.decode("#EC4899");
    private static final Color ENTRY_BG = Color.WHITE;
    private static final Color OK_COLOR = Color.decode("#22C55E");
    private static final Color WARN_COLOR = Color.decode("#F59E0B");
    private static final Color ERROR_COLOR = Color.decode("#EF4444");

    public interface StartListener {
        void onStart(int port);
    }

    private StartListener startListener;

    private JTextField portField;
    private JButton startButton;
    private JLabel statusLabel;

    private JLabel algorithmValue;
    private JLabel stateValue;
    private JLabel messageValue;
    private JLabel detailValue;

    private JTextArea logArea;

    public ReceptorWindow() {
        super("Receptor");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(720, 720);
        setLocationRelativeTo(null);
        getContentPane().setBackground(BACKGROUND);
        build();
    }

    public void setOnStart(StartListener listener) {
        this.startListener = listener;
    }

    private void build() {
        JPanel container = new JPanel();
        container.setLayout(new BoxLayout(container, BoxLayout.Y_AXIS));
        container.setBackground(BACKGROUND);
        container.setBorder(new EmptyBorder(25, 35, 25, 35));

        JLabel icon = new JLabel("📬");
        icon.setFont(new Font("SansSerif", Font.PLAIN, 42));
        icon.setAlignmentX(Component.CENTER_ALIGNMENT);
        container.add(icon);
        container.add(Box.createVerticalStrut(8));

        JLabel title = new JLabel("RECEPTOR");
        title.setFont(new Font("Helvetica", Font.BOLD, 32));
        title.setForeground(TITLE_COLOR);
        title.setAlignmentX(Component.CENTER_ALIGNMENT);
        container.add(title);

        JLabel subtitle = new JLabel("Laboratorio de Redes");
        subtitle.setFont(new Font("Helvetica", Font.PLAIN, 16));
        subtitle.setForeground(TEXT);
        subtitle.setAlignmentX(Component.CENTER_ALIGNMENT);
        container.add(subtitle);
        container.add(Box.createVerticalStrut(20));

        container.add(buildPortRow());
        container.add(Box.createVerticalStrut(10));

        statusLabel = new JLabel("Ingresa un puerto y presiona \"Escuchar\".");
        statusLabel.setFont(new Font("Helvetica", Font.PLAIN, 13));
        statusLabel.setForeground(TEXT);
        statusLabel.setAlignmentX(Component.LEFT_ALIGNMENT);
        container.add(statusLabel);
        container.add(Box.createVerticalStrut(15));

        container.add(buildSummaryPanel());
        container.add(Box.createVerticalStrut(15));

        container.add(buildLogPanel());

        setContentPane(container);
    }

    private JPanel buildPortRow() {
        JPanel row = new JPanel();
        row.setLayout(new BoxLayout(row, BoxLayout.X_AXIS));
        row.setBackground(BACKGROUND);
        row.setAlignmentX(Component.LEFT_ALIGNMENT);
        row.setMaximumSize(new Dimension(Integer.MAX_VALUE, 45));

        JLabel label = new JLabel("Puerto:");
        label.setFont(new Font("Helvetica", Font.BOLD, 14));
        label.setForeground(TEXT);

        portField = new JTextField("5000");
        portField.setFont(new Font("Helvetica", Font.PLAIN, 14));
        portField.setBackground(ENTRY_BG);
        portField.setBorder(BorderFactory.createCompoundBorder(
                new LineBorder(BORDER_COLOR, 2, true),
                new EmptyBorder(6, 10, 6, 10)
        ));
        portField.setMaximumSize(new Dimension(140, 40));

        startButton = new JButton("Escuchar");
        startButton.setFont(new Font("Helvetica", Font.BOLD, 14));
        startButton.setForeground(Color.WHITE);
        startButton.setBackground(BUTTON_COLOR);
        startButton.setFocusPainted(false);
        startButton.setBorder(new EmptyBorder(8, 20, 8, 20));
        startButton.addActionListener(event -> handleStartClicked());

        row.add(label);
        row.add(Box.createHorizontalStrut(10));
        row.add(portField);
        row.add(Box.createHorizontalStrut(15));
        row.add(startButton);

        return row;
    }

    private JPanel buildSummaryPanel() {
        JPanel panel = new JPanel(new GridLayout(4, 1, 0, 6));
        panel.setBackground(ENTRY_BG);
        panel.setAlignmentX(Component.LEFT_ALIGNMENT);
        panel.setBorder(BorderFactory.createCompoundBorder(
                new LineBorder(BORDER_COLOR, 2, true),
                new EmptyBorder(12, 15, 12, 15)
        ));
        panel.setMaximumSize(new Dimension(Integer.MAX_VALUE, 140));

        algorithmValue = createSummaryLine(panel, "Algoritmo:");
        stateValue = createSummaryLine(panel, "Estado:");
        messageValue = createSummaryLine(panel, "Mensaje:");
        detailValue = createSummaryLine(panel, "Detalle:");

        return panel;
    }

    private JLabel createSummaryLine(JPanel panel, String labelText) {
        JPanel line = new JPanel(new BorderLayout(10, 0));
        line.setBackground(ENTRY_BG);

        JLabel label = new JLabel(labelText);
        label.setFont(new Font("Helvetica", Font.BOLD, 13));
        label.setForeground(TEXT);
        label.setPreferredSize(new Dimension(90, 20));

        JLabel value = new JLabel("—");
        value.setFont(new Font("Helvetica", Font.PLAIN, 13));
        value.setForeground(TEXT);

        line.add(label, BorderLayout.WEST);
        line.add(value, BorderLayout.CENTER);
        panel.add(line);

        return value;
    }

    private JScrollPane buildLogPanel() {
        logArea = new JTextArea();
        logArea.setEditable(false);
        logArea.setFont(new Font("Monospaced", Font.PLAIN, 12));
        logArea.setBackground(Color.decode("#F8FAFC"));
        logArea.setForeground(TEXT);
        logArea.setLineWrap(true);
        logArea.setWrapStyleWord(true);
        logArea.setBorder(new EmptyBorder(10, 10, 10, 10));

        JScrollPane scrollPane = new JScrollPane(logArea);
        scrollPane.setBorder(new LineBorder(BORDER_COLOR, 2, true));
        scrollPane.setAlignmentX(Component.LEFT_ALIGNMENT);

        return scrollPane;
    }

    private void handleStartClicked() {
        String text = portField.getText().trim();
        int port;
        try {
            port = Integer.parseInt(text);
        } catch (NumberFormatException error) {
            JOptionPane.showMessageDialog(this, "El puerto debe ser un número.", "Error", JOptionPane.ERROR_MESSAGE);
            return;
        }

        portField.setEnabled(false);
        startButton.setEnabled(false);
        startButton.setText("Escuchando...");
        statusLabel.setForeground(TEXT);
        statusLabel.setText("Conectando en el puerto " + port + "...");

        if (startListener != null) {
            startListener.onStart(port);
        }
    }

    /** Llamar solo desde el hilo de Swing (usar SwingUtilities.invokeLater). */
    public void showListening(int port) {
        statusLabel.setForeground(OK_COLOR);
        statusLabel.setText("Escuchando en el puerto " + port + ". Esperando tramas...");
    }

    /** Llamar solo desde el hilo de Swing (usar SwingUtilities.invokeLater). */
    public void showError(String message) {
        statusLabel.setForeground(ERROR_COLOR);
        statusLabel.setText(message);
        portField.setEnabled(true);
        startButton.setEnabled(true);
        startButton.setText("Escuchar");
    }

    /** Llamar solo desde el hilo de Swing (usar SwingUtilities.invokeLater). */
    public void showFrame(Frame frame) {
        algorithmValue.setText(String.valueOf(frame.algorithm));

        if (!frame.corrupted) {
            stateValue.setForeground(OK_COLOR);
            stateValue.setText("Sin errores");
        } else if (frame.corrected) {
            stateValue.setForeground(WARN_COLOR);
            stateValue.setText("Error detectado y corregido");
        } else {
            stateValue.setForeground(ERROR_COLOR);
            stateValue.setText("Error detectado, NO corregible");
        }

        messageValue.setText(frame.message != null ? frame.message : "(no decodificable)");
        detailValue.setText(frame.errorDetail != null ? frame.errorDetail : "");

        logArea.append(formatLogBlock(frame));
        logArea.setCaretPosition(logArea.getDocument().getLength());
    }

    private String formatLogBlock(Frame frame) {
        String timestamp = new SimpleDateFormat("HH:mm:ss").format(new Date());
        StringBuilder block = new StringBuilder();

        block.append("========== [").append(timestamp).append("] TRANSMISSION ==========\n");
        block.append("Trama recibida (").append(frame.rawPayload.length()).append(" bits).\n\n");

        block.append("========== LINK ==========\n");
        block.append("Algoritmo detectado : ").append(frame.algorithm).append("\n");
        block.append("Datos               : ").append(frame.dataBits).append("\n");
        block.append("Integridad recibida : ").append(frame.receivedIntegrity).append("\n\n");

        block.append("========== PRESENTATION ==========\n");
        block.append(frame.corrupted && !frame.corrected ? "(no decodificable)" : frame.message).append("\n\n");

        block.append("========== APPLICATION ==========\n");
        block.append("Detalle             : ").append(frame.errorDetail).append("\n");
        if (frame.corrupted && !frame.corrected) {
            block.append("*** ERROR: se detectaron errores y no fue posible corregirlos. ***\n");
        } else {
            block.append("Mensaje recibido    : ").append(frame.message).append("\n");
        }
        block.append("\n");

        return block.toString();
    }
}