from application import ApplicationLayer
from presentation import PresentationLayer
from link import LinkLayer
#from noise import NoiseLayer
#from transport import SocketClient

#main para application y presentation
def main():

    app = ApplicationLayer()
    presentation = PresentationLayer()
    link = LinkLayer()

    frame = app.request_message()

    if frame is None:
        return

    frame = presentation.encode(frame)
    frame.metadata["ascii"] = frame.payload

    frame = link.add_integrity(frame)

    print("\n===== FRAME =====")
    print(f"Mensaje    : {frame.message}")
    print(f"Algoritmo  : {frame.algorithm.value}")
    print(f"Puerto     : {frame.destination_port}")
    print(f"BER        : {frame.ber}")
    print(f"Payload    : {frame.payload}")
    print(f"Integridad : {frame.integrity}")

if __name__ == "__main__":
    main()