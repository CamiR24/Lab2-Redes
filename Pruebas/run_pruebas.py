"""
Script de pruebas automatizadas para el Laboratorio 2 (CC3067).

Simula cientos de transmisiones variando los 4 factores que pide el
enunciado: tamaño del mensaje, probabilidad de error (BER), algoritmo
utilizado (CRC32 / HAMMING) y mide el overhead de cada uno. Genera un CSV
con los resultados y varias gráficas listas para el reporte.

Cómo se simula cada transmisión:
- La codificación (Presentación) y el cálculo de integridad (Enlace,
  calcular_integridad) y el ruido usan DIRECTAMENTE el código real del
  Emisor (Emisor/presentation, Emisor/link, Emisor/noise) — el mismo que
  se entrega en el laboratorio.
- La verificación/corrección del lado del receptor (Enlace,
  verificar_integridad / corregir_mensaje) usa una traducción línea por
  línea de la lógica Java del Receptor (Receptor/src/link/...), ya
  validada contra el Emisor real en pruebas de integración anteriores.
  Se reimplementa en Python únicamente para poder correr miles de pruebas
  en segundos sin tener que abrir sockets y procesos Java repetidamente;
  el funcionamiento end-to-end real (con sockets) ya se probó manualmente
  con la GUI de ambos lados.

Uso:
    python3 run_pruebas.py
"""
import csv
import os
import random
import sys
import time
import zlib

import matplotlib.pyplot as plt
import pandas as pd

# ---------------------------------------------------------------------------
# Acceso al código real del Emisor
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EMISOR_DIR = os.path.join(SCRIPT_DIR, "..", "Emisor")
sys.path.insert(0, EMISOR_DIR)

from models.frame import Frame, Algorithm          # noqa: E402
from presentation.presentation_layer import PresentationLayer  # noqa: E402
from link.link_layer import LinkLayer               # noqa: E402
from noise.noise_layer import NoiseLayer            # noqa: E402

PRESENTATION = PresentationLayer()
LINK = LinkLayer()
NOISE = NoiseLayer()

HEADER_LENGTH = 8
HEADER_CODES = {"00000001": "CRC32", "00000010": "HAMMING"}


# ---------------------------------------------------------------------------
# Lógica del receptor (traducción de Receptor/src/link/... a Python)
# ---------------------------------------------------------------------------
def crc32_calculate(data_bits: str) -> str:
    if not data_bits:
        return format(zlib.crc32(b"") & 0xFFFFFFFF, "032b")
    data = int(data_bits, 2).to_bytes(len(data_bits) // 8, "big")
    return format(zlib.crc32(data) & 0xFFFFFFFF, "032b")


def hamming_required_parity_bits_from_total_length(total_length: int) -> int:
    r = 1
    while (1 << r) < (total_length + 1):
        r += 1
    return r


def build_position_map(m: int, r: int):
    """Mapea cada índice de bit de dato (0-based) a su posición virtual
    (1-based) en un Hamming clásico intercalado, en O(m + r) en vez de
    llamar una función O(posición) por cada bit (igual resultado, más
    rápido para poder correr miles de pruebas)."""
    n = m + r
    data_to_pos = [0] * m
    idx = 0
    for pos in range(1, n + 1):
        if (pos & (pos - 1)) != 0:  # no es potencia de 2
            data_to_pos[idx] = pos
            idx += 1
    pos_to_idx = {pos: i for i, pos in enumerate(data_to_pos)}
    return data_to_pos, pos_to_idx


def hamming_calculate_parity(data_bits: str, r: int, data_to_pos) -> str:
    parity = [0] * r
    for idx, bit in enumerate(data_bits):
        if bit == "1":
            vp = data_to_pos[idx]
            for k in range(r):
                if (vp >> k) & 1:
                    parity[k] ^= 1
    return "".join(str(parity[k]) for k in range(r - 1, -1, -1))


def hamming_verify_and_correct(data: str, received_parity: str, data_to_pos, pos_to_idx):
    r = len(received_parity)
    recalculated = hamming_calculate_parity(data, r, data_to_pos)
    syndrome = int(received_parity, 2) ^ int(recalculated, 2)

    if syndrome == 0:
        return {"category": "ok", "data": data}

    if (syndrome & (syndrome - 1)) == 0:
        # error en un bit de paridad; los datos están intactos
        return {"category": "ok_paridad", "data": data}

    data_index = pos_to_idx.get(syndrome, -1)
    if data_index < 0:
        return {"category": "no_corregible", "data": data}

    corrected = list(data)
    corrected[data_index] = "1" if corrected[data_index] == "0" else "0"
    return {"category": "corregido", "data": "".join(corrected)}


def receptor_procesar(raw_payload: str):
    """Simula Transmisión->Enlace->Presentación del lado del receptor."""
    if len(raw_payload) < HEADER_LENGTH:
        return {"category": "trama_invalida", "message": None}

    header = raw_payload[:HEADER_LENGTH]
    rest = raw_payload[HEADER_LENGTH:]
    algorithm = HEADER_CODES.get(header)

    if algorithm is None:
        return {"category": "cabecera_perdida", "message": None, "algorithm": "DESCONOCIDO"}

    if algorithm == "CRC32":
        integrity_len = 32
        if len(rest) <= integrity_len:
            return {"category": "trama_invalida", "message": None, "algorithm": algorithm}
        data = rest[:-integrity_len]
        received_integrity = rest[-integrity_len:]
        if len(data) % 8 != 0:
            # El ruido corrompió la cabecera y una trama de otro algoritmo
            # se interpretó por error como CRC32.
            return {"category": "trama_invalida", "message": None, "algorithm": algorithm}
        recalculated = crc32_calculate(data)
        if recalculated == received_integrity:
            category = "ok"
        else:
            category = "detectado_no_corregido"
    else:  # HAMMING
        total_length = len(rest)
        r = hamming_required_parity_bits_from_total_length(total_length)
        m = total_length - r
        if m < 0:
            return {"category": "trama_invalida", "message": None, "algorithm": algorithm}
        data = rest[:m]
        received_parity = rest[m:]
        data_to_pos, pos_to_idx = build_position_map(m, r)
        result = hamming_verify_and_correct(data, received_parity, data_to_pos, pos_to_idx)
        category = result["category"]
        data = result["data"]

    if category in ("ok", "ok_paridad", "corregido"):
        if len(data) % 8 != 0:
            return {"category": "trama_invalida", "message": None, "algorithm": algorithm}
        message = "".join(chr(int(data[i:i + 8], 2)) for i in range(0, len(data), 8))
        return {"category": category, "message": message, "algorithm": algorithm}

    return {"category": category, "message": None, "algorithm": algorithm}


# ---------------------------------------------------------------------------
# Simulación de una transmisión completa (Emisor real -> Receptor)
# ---------------------------------------------------------------------------
CHARSET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ .,!?"


def random_message(length: int) -> str:
    return "".join(random.choice(CHARSET) for _ in range(length))


def simular_transmision(message: str, algorithm: Algorithm, ber: float):
    frame = Frame(message=message, algorithm=algorithm, ber=ber)
    frame = PRESENTATION.encode(frame)
    frame = LINK.add_integrity(frame)  # cabecera + datos + integridad (código real del Emisor)

    total_bits_sin_ruido = len(frame.payload)
    integrity_bits = len(frame.integrity)
    data_bits = len(frame.payload) - HEADER_LENGTH - integrity_bits
    overhead_pct = (integrity_bits + HEADER_LENGTH) / total_bits_sin_ruido * 100

    frame = NOISE.apply(frame)  # ruido real del Emisor
    resultado = receptor_procesar(frame.payload)

    exito = resultado["message"] == message

    return {
        "algoritmo": algorithm.value,
        "tamano_mensaje_chars": len(message),
        "ber": ber,
        "categoria": resultado["category"],
        "exito": exito,
        "overhead_pct": overhead_pct,
        "data_bits": data_bits,
        "integrity_bits": integrity_bits,
        "total_bits": total_bits_sin_ruido,
    }


# ---------------------------------------------------------------------------
# Barrido de experimentos
# ---------------------------------------------------------------------------
def correr_experimentos(seed=42, trials_por_combinacion=150):
    random.seed(seed)

    tamanos = [5, 20, 50, 100]
    bers = [0.0, 0.001, 0.002, 0.005, 0.01, 0.02, 0.03, 0.05, 0.08, 0.1]
    algoritmos = [Algorithm.CRC32, Algorithm.HAMMING]

    registros = []
    total_combos = len(tamanos) * len(bers) * len(algoritmos)
    combo_actual = 0
    inicio = time.time()

    for tamano in tamanos:
        for algoritmo in algoritmos:
            for ber in bers:
                combo_actual += 1
                for _ in range(trials_por_combinacion):
                    mensaje = random_message(tamano)
                    registros.append(simular_transmision(mensaje, algoritmo, ber))
                print(f"[{combo_actual}/{total_combos}] tamano={tamano} "
                      f"algoritmo={algoritmo.value} ber={ber} -> "
                      f"{trials_por_combinacion} pruebas ({time.time() - inicio:.1f}s acumulado)")

    return pd.DataFrame(registros)


def agregar(df: pd.DataFrame) -> pd.DataFrame:
    grupo = df.groupby(["algoritmo", "tamano_mensaje_chars", "ber"])
    resumen = grupo.agg(
        n=("exito", "size"),
        tasa_exito=("exito", "mean"),
        overhead_pct_prom=("overhead_pct", "mean"),
    ).reset_index()

    # Desglose de categorías (proporción de cada resultado posible)
    categorias = df.groupby(["algoritmo", "tamano_mensaje_chars", "ber", "categoria"]).size()
    categorias = categorias.reset_index(name="conteo")
    totales = categorias.groupby(["algoritmo", "tamano_mensaje_chars", "ber"])["conteo"].transform("sum")
    categorias["proporcion"] = categorias["conteo"] / totales

    return resumen, categorias


# ---------------------------------------------------------------------------
# Gráficas
# ---------------------------------------------------------------------------
COLOR = {"CRC32": "#3B82F6", "HAMMING": "#EC4899"}


def graficar_exito_vs_ber_por_tamano(resumen: pd.DataFrame, out_dir: str):
    tamanos = sorted(resumen["tamano_mensaje_chars"].unique())
    fig, axes = plt.subplots(1, len(tamanos), figsize=(5 * len(tamanos), 4.5), sharey=True)

    for ax, tamano in zip(axes, tamanos):
        for algoritmo in ["CRC32", "HAMMING"]:
            datos = resumen[(resumen.tamano_mensaje_chars == tamano) & (resumen.algoritmo == algoritmo)]
            datos = datos.sort_values("ber")
            ax.plot(datos.ber, datos.tasa_exito * 100, marker="o", label=algoritmo, color=COLOR[algoritmo])
        ax.set_title(f"Mensaje de {tamano} caracteres")
        ax.set_xlabel("BER (probabilidad de error por bit)")
        ax.set_ylim(-5, 105)
        ax.grid(alpha=0.3)

    axes[0].set_ylabel("Tasa de éxito (%)\n(mensaje recibido == mensaje original)")
    axes[0].legend()
    fig.suptitle("Tasa de éxito vs. BER, por algoritmo y tamaño de mensaje")
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "exito_vs_ber_por_tamano.png"), dpi=150)
    plt.close(fig)


def graficar_desglose(categorias: pd.DataFrame, algoritmo: str, tamano: int, out_dir: str):
    datos = categorias[(categorias.algoritmo == algoritmo) & (categorias.tamano_mensaje_chars == tamano)]
    tabla = datos.pivot_table(index="ber", columns="categoria", values="proporcion", fill_value=0)
    tabla = tabla.sort_index()

    fig, ax = plt.subplots(figsize=(7, 4.5))
    tabla.plot.area(ax=ax, alpha=0.85)
    ax.set_xlabel("BER (probabilidad de error por bit)")
    ax.set_ylabel("Proporción de tramas")
    ax.set_title(f"Desglose de resultados — {algoritmo}, mensaje de {tamano} caracteres")
    ax.legend(title="Resultado", loc="center left", bbox_to_anchor=(1.0, 0.5))
    fig.tight_layout()
    nombre = f"desglose_{algoritmo.lower()}_{tamano}c.png"
    fig.savefig(os.path.join(out_dir, nombre), dpi=150)
    plt.close(fig)


def graficar_overhead_vs_tamano(resumen: pd.DataFrame, out_dir: str):
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for algoritmo in ["CRC32", "HAMMING"]:
        datos = resumen[resumen.algoritmo == algoritmo]
        datos = datos.groupby("tamano_mensaje_chars")["overhead_pct_prom"].mean().reset_index()
        datos = datos.sort_values("tamano_mensaje_chars")
        ax.plot(datos.tamano_mensaje_chars, datos.overhead_pct_prom, marker="o",
                label=algoritmo, color=COLOR[algoritmo])
    ax.set_xlabel("Tamaño del mensaje (caracteres)")
    ax.set_ylabel("Overhead (%)\n(bits de cabecera+integridad / bits totales)")
    ax.set_title("Overhead vs. tamaño del mensaje")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "overhead_vs_tamano.png"), dpi=150)
    plt.close(fig)


def graficar_exito_vs_tamano(resumen: pd.DataFrame, out_dir: str, ber_fijo=0.02):
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for algoritmo in ["CRC32", "HAMMING"]:
        datos = resumen[(resumen.algoritmo == algoritmo) & (resumen.ber == ber_fijo)]
        datos = datos.sort_values("tamano_mensaje_chars")
        ax.plot(datos.tamano_mensaje_chars, datos.tasa_exito * 100, marker="o",
                label=algoritmo, color=COLOR[algoritmo])
    ax.set_xlabel("Tamaño del mensaje (caracteres)")
    ax.set_ylabel("Tasa de éxito (%)")
    ax.set_title(f"Tasa de éxito vs. tamaño del mensaje (BER fijo = {ber_fijo})")
    ax.legend()
    ax.grid(alpha=0.3)
    ax.set_ylim(-5, 105)
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "exito_vs_tamano.png"), dpi=150)
    plt.close(fig)


def main():
    out_dir = SCRIPT_DIR
    print("Corriendo experimentos (esto puede tardar un par de minutos)...\n")

    df = correr_experimentos()

    crudos_path = os.path.join(out_dir, "resultados_crudos.csv")
    df.to_csv(crudos_path, index=False)
    print(f"\nGuardado: {crudos_path} ({len(df)} filas)")

    resumen, categorias = agregar(df)
    resumen_path = os.path.join(out_dir, "resultados_agregados.csv")
    resumen.to_csv(resumen_path, index=False)
    print(f"Guardado: {resumen_path}")

    print("\nGenerando gráficas...")
    graficar_exito_vs_ber_por_tamano(resumen, out_dir)
    graficar_overhead_vs_tamano(resumen, out_dir)
    graficar_exito_vs_tamano(resumen, out_dir)
    graficar_desglose(categorias, "HAMMING", 50, out_dir)
    graficar_desglose(categorias, "CRC32", 50, out_dir)

    print("\nListo. Archivos generados en:", out_dir)


if __name__ == "__main__":
    main()
