# Pruebas

Script de pruebas automatizadas para el Laboratorio 2. Genera cientos de
transmisiones simuladas variando los 4 factores que pide el enunciado
(tamaño del mensaje, BER, algoritmo, overhead) y produce gráficas listas
para el reporte.

## Cómo correrlo

```bash
cd Pruebas
pip install matplotlib pandas
python3 run_pruebas.py
```

Tarda cerca de 15-20 segundos y corre 12,000 transmisiones simuladas
(4 tamaños de mensaje × 10 valores de BER × 2 algoritmos × 150 repeticiones).

## Metodología

- La codificación (Presentación), el cálculo de integridad (Enlace) y el
  ruido usan **directamente el código real del Emisor** (`Emisor/presentation`,
  `Emisor/link`, `Emisor/noise`) — el mismo que se entrega en el
  laboratorio, no una reimplementación.
- La verificación/corrección del lado del receptor es una traducción línea
  por línea de la lógica Java real (`Receptor/src/link/...`), ya validada
  contra el Emisor en pruebas de integración manuales. Se reimplementa en
  Python solo para poder correr miles de transmisiones en segundos, sin
  tener que levantar sockets y procesos Java repetidamente. El
  funcionamiento real de extremo a extremo (con sockets, entre el Emisor en
  Python y el Receptor en Java) ya se demostró manualmente con las GUIs de
  ambos lados.
- Cada "transmisión" se repite 150 veces por combinación de
  (tamaño, algoritmo, BER) con mensajes aleatorios distintos, para tener
  una muestra estadísticamente razonable.

## Archivos generados

- `resultados_crudos.csv`: una fila por cada una de las 12,000 pruebas.
- `resultados_agregados.csv`: tasa de éxito y overhead promedio por
  combinación de (algoritmo, tamaño, BER).
- `exito_vs_ber_por_tamano.png`: tasa de éxito vs. BER, un panel por
  tamaño de mensaje, comparando CRC32 vs Hamming.
- `exito_vs_tamano.png`: tasa de éxito vs. tamaño del mensaje, con BER
  fijo (0.02).
- `overhead_vs_tamano.png`: overhead (%) vs. tamaño del mensaje, por
  algoritmo.
- `desglose_hamming_50c.png` / `desglose_crc32_50c.png`: para mensajes de
  50 caracteres, qué proporción de tramas termina en cada categoría
  posible (sin errores, corregido, detectado sin corregir, no corregible,
  cabecera perdida) según el BER.

## Categorías de resultado

- `ok`: no hubo errores (o Hamming no los tuvo que corregir).
- `ok_paridad`: Hamming detectó un error, pero cayó en un bit de paridad;
  los datos están intactos.
- `corregido`: Hamming detectó y corrigió un error de 1 bit en los datos.
- `no_corregible`: se detectó un error pero no se pudo corregir (CRC32
  siempre cae aquí cuando hay error, ya que es solo de detección; Hamming
  cae aquí cuando hay más de 1 bit dañado).
- `cabecera_perdida`: el ruido corrompió los 8 bits de la cabecera y el
  receptor ya no puede saber qué algoritmo se usó. Ni CRC32 ni Hamming
  protegen la cabecera, así que esto le puede pasar a cualquiera de los
  dos y, con BER alto, termina siendo la causa más común de fallo (ver
  `desglose_*.png`).
- `trama_invalida`: caso borde donde una cabecera corrompida hace que la
  trama se interprete con el algoritmo equivocado y el tamaño de datos
  resultante queda mal alineado; se descarta en vez de arriesgar una
  decodificación incorrecta.

## Hallazgos para discutir en el reporte

1. **Hamming le gana a CRC32 en tasa de éxito** en todos los tamaños de
   mensaje probados, porque además de detectar puede corregir errores de 1
   bit — CRC32 los detecta pero se rinde.
2. **La ventaja de Hamming se reduce con mensajes más grandes.** Esta
   implementación aplica Hamming sobre todo el mensaje como un solo bloque
   (para cumplir la fórmula genérica del enunciado), así que solo garantiza
   corregir 1 bit por trama completa. Con mensajes largos, es más probable
   que caigan 2+ bits dañados en la misma trama, y ahí Hamming ya no puede
   corregir de forma confiable (ver categoría `no_corregible` y cómo crece
   con el tamaño del mensaje).
3. **Hamming tiene menos overhead que CRC32** en todos los tamaños: los
   bits de paridad crecen logarítmicamente con el mensaje, mientras que
   CRC32 siempre agrega 32 bits fijos. Para mensajes cortos, el overhead de
   CRC32 puede llegar a ser la mitad de la trama.
4. **La cabecera es un punto ciego para ambos algoritmos.** Ninguno la
   protege, así que con BER alto la causa más común de "fallo" no es que
   el algoritmo no pueda corregir el error, sino que se pierde el
   identificador del algoritmo (`cabecera_perdida`) y la trama se descarta
   por completo.
