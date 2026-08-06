from dataclasses import dataclass, field
from enum import Enum

class Algorithm(Enum):
    CRC32 = "CRC32"

# todas las capas reciben el mismo objeto y solamente modifican el atributo que les corresponde
@dataclass
class Frame:
    #info ingresada por el usuario
    message: str = ""
    algorithm: Algorithm = Algorithm.CRC32
    #destino
    destination_port: int = 5000
    #probabilidad de error
    ber: float = 0.0
    #trama binaria que va evolucionando
    payload: str = ""
    #información de integridad CRC32
    integrity: str = ""
    #Info adicional
    metadata: dict = field(default_factory=dict)