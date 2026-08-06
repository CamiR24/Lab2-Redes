from models.frame import Frame
import random

class NoiseLayer:

    def apply(self, frame: Frame) -> Frame:
        noisy_payload = ""
        flipped_bits = 0

        for bit in frame.payload:
            if random.random() < frame.ber:
                noisy_payload += "1" if bit == "0" else "0"
                flipped_bits += 1
            else:
                noisy_payload += bit

        frame.metadata["payload_before_noise"] = frame.payload
        frame.metadata["payload_after_noise"] = noisy_payload
        frame.metadata["flipped_bits"] = flipped_bits
        frame.payload = noisy_payload

        return frame