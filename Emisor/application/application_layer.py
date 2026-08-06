from models.frame import Frame
from application.main_window import MainWindow

class ApplicationLayer:

    def request_message(self):

        window = MainWindow()

        data = window.run()

        frame = Frame()

        frame.message = data["message"]
        frame.algorithm = data["algorithm"]
        frame.destination_port = data["port"]
        frame.ber = data["ber"]

        return frame