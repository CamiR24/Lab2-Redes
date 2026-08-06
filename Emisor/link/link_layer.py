from models.frame import Frame, Algorithm
from link.algorithms.crc32 import CRC32
from link.algorithms.algoritmo2 import Hamming


class LinkLayer:

    HEADER_CODES = {
        Algorithm.CRC32: "00000001",
        Algorithm.HAMMING: "00000010"
    }

    def __init__(self):
        self.crc32 = CRC32()
        self.hamming = Hamming()

    def add_integrity(self, frame: Frame) -> Frame:
        if frame.algorithm == Algorithm.CRC32:
            frame = self.crc32.encode(frame)
        elif frame.algorithm == Algorithm.HAMMING:
            frame = self.hamming.encode(frame)
        else:
            raise ValueError(
                f"Algoritmo no soportado: {frame.algorithm}"
            )

        header = self.build_header(frame)
        frame.payload = (
            header +
            frame.payload +
            frame.integrity
        )
        return frame

    def build_header(self, frame: Frame) -> str:
        return self.HEADER_CODES[frame.algorithm]