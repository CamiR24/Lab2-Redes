# Lab2-Redes — Laboratorio de la capa de Enlace de Datos

Implementación de un Emisor y un Receptor que se comunican por sockets TCP,
codificando el mensaje en binario y aplicando un algoritmo de detección o
corrección de errores en la capa de Enlace.

- **Emisor**: Python 3 (`Emisor/`)
- **Receptor**: Java (`Receptor/`)

## Arquitectura

Ambos lados siguen la misma idea de capas, cada una modificando solo lo que
le corresponde de una misma trama (`Frame`):

**Emisor**

```
Aplicación → Presentación → Enlace → Ruido → Transporte
```

**Receptor**

```
Transporte → Enlace → Presentación → Aplicación
```

## Protocolo

Toda la comunicación se hace en binario (texto de '0'/'1' enviado por el
socket). La trama tiene el siguiente formato:

```
[Cabecera (8 bits)][Datos][Integridad]
```

- **Cabecera**: identifica qué algoritmo se usó, para que el receptor sepa
  cómo interpretar el resto de la trama.
- **Datos**: el mensaje codificado en ASCII binario (8 bits por carácter).
- **Integridad**: información generada por el algoritmo seleccionado
  (CRC de 32 bits, o bits de paridad de Hamming).

## Algoritmos soportados

| Algoritmo | Cabecera | Tipo de servicio | Tamaño de integridad |
|-----------|----------|-------------------|------------------------|
| CRC32     | `00000001` | Detección | 32 bits fijos |
| HAMMING   | `00000010` | Corrección | r bits, variable según el largo del mensaje |

- **CRC32**: polinomio estándar 0xEDB88320. Si el CRC recalculado no
  coincide con el recibido, el receptor reporta el error y **no** intenta
  corregirlo (CRC32 no tiene esa capacidad).
- **Hamming**: sistemático y generalizado a cualquier tamaño de mensaje m
  (no solo bloques fijos de 4 bits). Se calcula el mínimo r de bits de
  paridad tal que `(m + r + 1) <= 2^r`, concatenados al final de los datos.
  El receptor recalcula la paridad y usa el síndrome (XOR) para saber qué
  pasó:
  - síndrome = 0 → sin errores.
  - síndrome = potencia de 2 → el error cayó en un bit de paridad, los
    datos están intactos.
  - cualquier otro valor → indica la posición exacta del bit de dato
    dañado, y se corrige automáticamente.

### Limitación conocida

Ni CRC32 ni Hamming protegen la **cabecera** (solo cubren los datos). Con
BER alto, un bit de la cabecera se puede corromper y el receptor ya no
puede saber qué algoritmo se usó ("cabecera desconocida"), perdiendo la
trama completa aunque el resto se hubiera podido corregir. Además, Hamming
solo garantiza corrección de **1 bit** por trama: si caen 2 o más bits
dañados en la misma trama, puede corregir mal (miscorrección) en vez de
detectar el problema. Ambos puntos son útiles para la discusión del
reporte.

## Cómo correrlo

Necesitas dos terminales. El **receptor debe estar escuchando antes** de
enviar el mensaje desde el emisor.

### 1. Receptor (Java)

Requiere JDK 11+.

```bash
cd Receptor
javac -d out $(find src -name "*.java")
java -cp out Main
```

Te va a pedir el puerto en el que escuchará (debe coincidir con el que
pongas en el emisor). Queda escuchando de forma continua: tras procesar
una trama, espera la siguiente.

> No subas la carpeta `Receptor/out/` a git — son los `.class` compilados
> (ver `.gitignore`).

### 2. Emisor (Python)

```bash
cd Emisor
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

Se abre una ventana donde eliges el mensaje, el algoritmo (CRC32 o
HAMMING, con el desplegable), el puerto (el mismo del receptor) y el BER
(probabilidad de error por bit; usa `0` para probar sin ruido, o algo como
`0.01`–`0.05` para ver detección/corrección en acción).

## Problemas comunes (macOS)

- **`Address already in use` en el puerto 5000**: en Mac, "AirPlay
  Receiver" usa ese puerto por defecto. Usa otro puerto (ej. `5050`) en
  ambos lados, o desactívalo en Configuración del Sistema → General →
  AirDrop y Handoff.
- **La ventana del emisor abre en blanco**: intenta redimensionarla o
  moverla (bug de renderizado de Tk). Si persiste, corre
  `python3 -c "import tkinter; print(tkinter.TkVersion)"`; si da `8.5`,
  estás usando el Tcl/Tk viejo del sistema. Instala Python vía Homebrew
  (que trae Tk 8.6+) y recrea el venv con ese Python:
  ```bash
  brew install python-tk@3.12
  /opt/homebrew/opt/python@3.12/bin/python3.12 -m venv venv   # Apple Silicon
  # /usr/local/opt/python@3.12/bin/python3.12 -m venv venv    # Intel
  source venv/bin/activate
  pip install -r requirements.txt
  ```

## Lenguajes

- Emisor: Python 3.13
- Receptor: Java 11+