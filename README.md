# Emisor - Laboratorio de Redes

## Descripción
Implementación del emisor para el laboratorio de la capa de Enlace de Datos.

El emisor implementa las siguientes capas:

- Aplicación
- Presentación
- Enlace
- Ruido
- Transporte

## Flujo

Aplicación
    ↓
Presentación
    ↓
Enlace
    ↓
Ruido
    ↓
Transporte

## Protocolo

Toda la comunicación entre el emisor y el receptor se realiza en binario.

La trama enviada tiene el siguiente formato:

[Cabecera][Datos][Integridad]

donde:

- Cabecera: información necesaria para interpretar la trama.
- Datos: mensaje codificado en ASCII binario.
- Integridad: información generada por el algoritmo seleccionado.

## Algoritmos soportados

- CRC32

## Lenguaje

Python 3.13