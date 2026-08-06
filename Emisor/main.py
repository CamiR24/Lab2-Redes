from application.application_layer import ApplicationLayer

#main solo para application
def main():

    application = ApplicationLayer()

    frame = application.request_message()

    print("\n===== FRAME GENERADO =====")
    print(f"Mensaje   : {frame.message}")
    print(f"Algoritmo : {frame.algorithm}")
    print(f"Puerto    : {frame.destination_port}")
    print(f"BER       : {frame.ber}")


if __name__ == "__main__":
    main()