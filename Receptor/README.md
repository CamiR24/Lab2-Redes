# Receptor - Laboratorio de Redes

## Descripción

Implementación del receptor para el laboratorio de la capa de Enlace de
Datos. Recibe la trama binaria enviada por el Emisor (Python), identifica
el algoritmo usado por la cabecera, verifica la integridad, corrige el
mensaje si el algoritmo lo permite, y lo muestra al usuario.

El receptor implementa las siguientes capas:

- Transmisión (`transport/SocketServer.java`): escucha en un puerto TCP y
  recibe la trama binaria como texto de '0'/'1'.
- Enlace (`link/LinkLayer.java` + `link/algorithms/`): separa
  cabecera/datos/integridad, verifica y corrige según el algoritmo.
- Presentación (`presentation/PresentationLayer.java`): decodifica ASCII
  binario a texto.
- Aplicación (`application/ApplicationLayer.java`): muestra el mensaje, o
  un error si se detectó un fallo que no se pudo corregir.

## Flujo

Transmisión → Enlace → Presentación → Aplicación

## Protocolo

Igual que en el Emisor: `[Cabecera(8 bits)][Datos][Integridad]`.

| Algoritmo | Cabecera  | Tipo de servicio | Longitud de integridad |
|-----------|-----------|------------------|-------------------------|
| CRC32     | 00000001  | Detección        | 32 bits fijos           |
| HAMMING   | 00000010  | Corrección       | r bits (variable, ver abajo) |

Para Hamming, el receptor no conoce de antemano cuántos bits son datos (m)
y cuántos son paridad (r); solo conoce la longitud total L = m + r. Como el
emisor siempre usa el mínimo r que cumple `(m + r + 1) <= 2^r`, y L = m + r,
esa condición equivale a `2^r >= L + 1`. El receptor recalcula r buscando el
mínimo valor que cumple esa desigualdad con la L recibida, lo cual
reconstruye exactamente el mismo r que usó el emisor.

## Algoritmos soportados

- **CRC32** (detección): si el CRC recalculado no coincide con el recibido,
  se marca la trama como corrupta y **no se corrige** (CRC32 no tiene esa
  capacidad).
- **Hamming** (corrección, sistemático y generalizado a cualquier tamaño de
  mensaje): se recalculan los bits de paridad y se compara contra los
  recibidos mediante un síndrome (XOR):
  - síndrome = 0 → sin errores.
  - síndrome = potencia de 2 → el error está en un bit de paridad; los
    datos están intactos.
  - cualquier otro síndrome → indica la posición exacta del bit de dato
    erróneo, que se corrige automáticamente (voltea ese bit).
  - Limitación esperada: si ocurre más de 1 bit de error simultáneo, el
    código puede corregir mal (miscorrección) o detectar un error no
    corregible, ya que Hamming solo garantiza corrección de 1 bit por
    trama. Vale la pena mostrar esto en las pruebas/discusión del reporte.

## Cómo compilar y ejecutar

Requiere JDK 11+ instalado.

```bash
cd Receptor
javac -d out $(find src -name "*.java")
java -cp out Main
```

El programa pedirá el puerto en el que debe escuchar (debe coincidir con
el puerto configurado en el Emisor al enviar el mensaje). El receptor queda
escuchando de forma continua: tras procesar una trama, vuelve a esperar la
siguiente.

También se puede pasar el puerto como argumento:

```bash
java -cp out Main 5000
```

## Lenguaje

Java 11+ (el Emisor está en Python, cumpliendo con el requisito de usar
lenguajes distintos en cada extremo).

## Nota de validación

En el entorno donde se generó este código no había un JDK completo
disponible para ejecutar `javac` directamente, así que la lógica de
Enlace (CRC32 y Hamming, incluyendo la detección/corrección con síndromes)
se validó primero transliterando el mismo algoritmo a Python y corriendo
pruebas de integración de extremo a extremo contra las tramas reales
generadas por el Emisor (con y sin bits corruptos, incluyendo errores en
datos, en paridad y en la cabecera). Todas las pruebas pasaron. Se
recomienda compilar y correr el receptor en tu máquina para la entrega
final y confirmar que compila sin errores en tu JDK.
