from application import ApplicationLayer
from presentation import PresentationLayer
from link import LinkLayer
from noise import NoiseLayer
from transport import SocketClient

def main():

    app = ApplicationLayer()
    presentation = PresentationLayer()
    link = LinkLayer()
    noise = NoiseLayer()
    transport = SocketClient()

    frame = app.request_message()

    if frame is None:
        return

    frame = presentation.encode(frame)
    frame.metadata["ascii"] = frame.payload
    print("\n========== PRESENTATION ==========")
    print(frame.payload)

    frame = link.add_integrity(frame)
    print("\n========== LINK ==========")
    print(f"Cabecera + Datos + Integridad:")
    print(frame.payload)
    print(f"\nCRC32:")
    print(frame.integrity)

    frame = noise.apply(frame)
    print("\n========== NOISE ==========")
    print(f"Antes : {frame.metadata['payload_before_noise']}")
    print(f"Después: {frame.payload}")
    print(f"Bits modificados: {frame.metadata['flipped_bits']}")

    transport.send(frame)

if __name__ == "__main__":
    main()