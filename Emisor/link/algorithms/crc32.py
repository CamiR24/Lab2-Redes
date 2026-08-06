from models.frame import Frame

class CRC32:

    def encode(self, frame: Frame) -> Frame:
        # Temporalmente no calculamos el CRC.
        frame.integrity = ""

        # La trama sigue siendo únicamente el mensaje en binario.
        frame.payload = frame.payload

        return frame