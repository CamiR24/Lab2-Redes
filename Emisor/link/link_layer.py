from models.frame import Frame, Algorithm
from link.algorithms.crc32 import CRC32

class LinkLayer:

    def __init__(self):
        self.crc32 = CRC32()

    def add_integrity(self, frame: Frame) -> Frame:
        if frame.algorithm == Algorithm.CRC32:
            return self.crc32.encode(frame)

        raise ValueError(f"Algoritmo no soportado: {frame.algorithm}")