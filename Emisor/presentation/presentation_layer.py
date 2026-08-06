from models.frame import Frame

class PresentationLayer:

    def encode(self, frame: Frame) -> Frame:
        binary = ""

        for character in frame.message:
            binary += format(ord(character), "08b")

        frame.payload = binary

        return frame

    def decode(self, frame: Frame) -> Frame:
        message = ""

        for i in range(0, len(frame.payload), 8):
            byte = frame.payload[i:i + 8]
            message += chr(int(byte, 2))

        frame.message = message

        return frame