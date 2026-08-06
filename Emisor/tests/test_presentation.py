from models.frame import Frame
from presentation import PresentationLayer

def test_ascii():
    frame = Frame(message="A")
    presentation = PresentationLayer()
    frame = presentation.encode(frame)
    assert frame.payload == "01000001"
    print("✓ PresentationLayer funciona correctamente")

if __name__ == "__main__":
    test_ascii()