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

    frame = link.add_integrity(frame)

    frame = noise.apply(frame)

    print("\n===== FRAME =====")
    print(f"Mensaje              : {frame.message}")
    print(f"Algoritmo            : {frame.algorithm.value}")
    print(f"Puerto               : {frame.destination_port}")
    print(f"BER                  : {frame.ber}")
    print(f"Payload              : {frame.metadata["payload_before_noise"]}")
    print(f"Integridad           : {frame.integrity}")
    print(f"Payload con ruido    : {frame.payload}")
    print(f"Bits modificados     : {frame.metadata["flipped_bits"]}")

    transport.send(frame)

if __name__ == "__main__":
    main()