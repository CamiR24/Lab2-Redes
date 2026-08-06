from models.frame import Frame
from noise import NoiseLayer

def test_noise():
    frame = Frame()
    frame.payload = "0000000000"
    frame.ber = 1
    noise = NoiseLayer()
    frame = noise.apply(frame)

    assert frame.payload == "1111111111"
    print("✓ NoiseLayer funciona")


if __name__ == "__main__":
    test_noise()