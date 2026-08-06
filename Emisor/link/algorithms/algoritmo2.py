from models.frame import Frame


class Hamming:
    """
    Código de Hamming sistemático y generalizado.

    Para un mensaje de m bits de datos, se calcula la cantidad mínima de
    bits de paridad r que cumple (m + r + 1) <= 2^r. A diferencia del
    Hamming(7,4) clásico (que trabaja en bloques fijos de 4 bits), aquí el
    código se aplica sobre TODO el mensaje como un único bloque, por lo que
    sirve para cualquier tamaño de mensaje m (cualquier Código (n, m)).

    En vez de intercalar los bits de paridad entre los datos (como en el
    Hamming clásico), se transmiten en forma sistemática: primero los datos
    originales y luego los r bits de paridad concatenados al final. Esto
    respeta el formato de trama pedido en el laboratorio
    (Cabecera + Datos + Integridad) y es compatible con la forma en que ya
    está implementado CRC32.

    Para no perder la capacidad de corrección al separar los bits de
    paridad de los datos, cada bit de dato se asocia a la posición que
    ocuparía en el código de Hamming "clásico" (intercalado), y se usa esa
    posición virtual para decidir en qué ecuaciones de paridad participa.
    De esta forma, el síndrome calculado en el receptor sigue indicando
    directamente la posición del bit erróneo (0 = sin error, potencia de 2 =
    error en un bit de paridad, cualquier otro valor = posición virtual del
    bit de dato a corregir).
    """

    def encode(self, frame: Frame) -> Frame:
        data_bits = frame.payload
        parity_bits = self._calculate_parity(data_bits)
        frame.integrity = parity_bits
        return frame

    def _calculate_parity(self, data_bits: str) -> str:
        m = len(data_bits)
        r = self._required_parity_bits(m)

        parity = [0] * r

        for data_index, bit in enumerate(data_bits):
            if bit == "0":
                continue
            virtual_position = self._virtual_position(data_index, r)
            for k in range(r):
                if (virtual_position >> k) & 1:
                    parity[k] ^= 1

        return "".join(str(bit) for bit in reversed(parity))

    def _required_parity_bits(self, m: int) -> int:
        r = 1
        while (m + r + 1) > (1 << r):
            r += 1
        return r

    def _virtual_position(self, data_index: int, r: int) -> int:
        """
        Traduce el índice de un bit de dato (0-based, en el mensaje sin
        bits de paridad) a la posición que tendría (1-based) dentro de un
        código de Hamming clásico donde los bits de paridad ocupan las
        posiciones que son potencia de 2 (1, 2, 4, 8, ...).
        """
        position = 1
        data_seen = 0

        while True:
            is_power_of_two = (position & (position - 1)) == 0
            if not is_power_of_two:
                if data_seen == data_index:
                    return position
                data_seen += 1
            position += 1
