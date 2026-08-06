from application import ApplicationLayer
from presentation import PresentationLayer
#from link import LinkLayer
#from noise import NoiseLayer
#from transport import SocketClient

#main para application y presentation
def main():

    app = ApplicationLayer()
    presentation = PresentationLayer()

    frame = app.request_message()

    if frame is None:
        return

    frame = presentation.encode(frame)

    print("\n===== FRAME =====")
    print("Mensaje:")
    print(frame.message)
    print("\nPayload:")
    print(frame.payload)

if __name__ == "__main__":
    main()