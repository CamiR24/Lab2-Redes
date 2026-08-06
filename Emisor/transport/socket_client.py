from models.frame import Frame
import socket

class SocketClient:

    def __init__(self, host="127.0.0.1"):
        self.host = host

    def send(self, frame: Frame):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                client.connect((self.host, frame.destination_port))
                client.sendall(frame.payload.encode())
                print("\nTrama enviada correctamente.")
        except ConnectionRefusedError:
            print("\nNo fue posible conectar con el receptor.")
        except Exception as error:
            print(f"\nError: {error}")