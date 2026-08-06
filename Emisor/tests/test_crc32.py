import zlib
from models.frame import Frame
from link.algorithms.crc32 import CRC32

def test_crc():
    frame = Frame()
    frame.payload = "01000001"   # A
    crc = CRC32()
    frame = crc.encode(frame)
    expected = format(
        zlib.crc32(b"A") & 0xFFFFFFFF,
        "032b"
    )
    print("Esperado :", expected)
    print("Obtenido :", frame.integrity)

    assert frame.integrity == expected
    print("✓ CRC32 correcto")


if __name__ == "__main__":
    test_crc()