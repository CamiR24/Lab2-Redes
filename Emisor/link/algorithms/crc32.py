from models.frame import Frame


class CRC32:

    POLYNOMIAL = 0xEDB88320

    def encode(self, frame: Frame) -> Frame:
        crc = self._calculate_crc(frame.payload)
        frame.integrity = format(crc, "032b")
        return frame

    def _calculate_crc(self, binary_message: str) -> int:
        if len(binary_message) % 8 != 0:
            raise ValueError(
                "El mensaje binario debe estar alineado a bytes."
            )
        
        data = int(binary_message, 2).to_bytes(
            (len(binary_message) + 7) // 8,
            byteorder="big"
        )

        crc = 0xFFFFFFFF

        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 1:
                    crc = (crc >> 1) ^ self.POLYNOMIAL
                else:
                    crc >>= 1
        crc ^= 0xFFFFFFFF

        return crc & 0xFFFFFFFF