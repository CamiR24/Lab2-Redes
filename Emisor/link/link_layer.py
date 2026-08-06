from models.frame import Frame, Algorithm
from link.algorithms.crc32 import CRC32


class LinkLayer:

    HEADER_CODES = {
        Algorithm.CRC32: "00000001"
    }

    def __init__(self):
        self.crc32 = CRC32()

    def add_integrity(self, frame: Frame) -> Frame:
        if frame.algorithm == Algorithm.CRC32:
            frame = self.crc32.encode(frame)
            header = self.build_header(frame)
            frame.payload = (
                header +
                frame.payload +
                frame.integrity
            )
            return frame

        raise ValueError(
            f"Algoritmo no soportado: {frame.algorithm}"
        )

    def build_header(self, frame: Frame) -> str:
        return self.HEADER_CODES[frame.algorithm]