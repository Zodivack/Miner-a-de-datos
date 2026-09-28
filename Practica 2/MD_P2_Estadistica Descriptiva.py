"""
████████████████████████████████████████████████████████████████████████████
█  ESTADISTICA DESCRIPTIVA - MCSR RANKED TEMPORADA 10                      █
████████████████████████████████████████████████████████████████████████████
"""

import pandas as pd
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from contextlib import contextmanager
import sys

BASE_DIR = Path("MCSR_Ranked")
FINAL_DIR = BASE_DIR / "data" / "final"

MAIN_DIR = FINAL_DIR / "main"
AUX_DIR = FINAL_DIR / "aux"

CSV_PARTIDAS = MAIN_DIR / "partidas.csv"
CSV_JUGADORES = MAIN_DIR / "jugadores.csv"
CSV_PARTIDA_JUGADORES = MAIN_DIR / "partida_jugadores.csv"

CSV_SEED_TORRES = AUX_DIR / "seed_torres.csv"
CSV_SEED_VARIACIONES = AUX_DIR / "seed_variaciones.csv"
CSV_CAMBIOS_ELO = AUX_DIR / "cambios_elo.csv"
CSV_COMPLETACIONES = AUX_DIR / "completaciones.csv"
CSV_LINEAS_TIEMPO = AUX_DIR / "lineas_tiempo.csv"
CSV_VOD = AUX_DIR / "vod.csv"

ACT2_DIR = BASE_DIR / "Act_2"
RESULTADOS_DIR = ACT2_DIR / "resultados"
RESULTADOS_DIR.mkdir(parents=True, exist_ok=True)

SALIDA_INVENTARIO = RESULTADOS_DIR / "inventario_variables.csv"
SALIDA_ESTADISTICAS = RESULTADOS_DIR / "estadistica_descriptiva.csv"
SALIDA_FRECUENCIAS = RESULTADOS_DIR / "frecuencias_categoricas.csv"
SALIDA_AGRUPADAS = RESULTADOS_DIR / "metricas_agrupadas.csv"
SALIDA_PARTICIPACIONES = RESULTADOS_DIR / "participaciones_pais.csv"
SALIDA_TEMPORAL = RESULTADOS_DIR / "analisis_temporal.csv"
SALIDA_RELACIONES = RESULTADOS_DIR / "entidades_relaciones.csv"
SALIDA_DIAGRAMA = RESULTADOS_DIR / "diagrama_entidades.png"
SALIDA_REPORTE = RESULTADOS_DIR / "reporte_act_2.txt"

VARIABLES_IDENTIFICADOR = {"id_partida", "jugador_uuid", "uuid_seed", "uuid_ganador", "vod_uuid"}
VARIABLES_INDICE = {"indice_jugador", "indice_torre", "indice_variacion", "indice_cambio", "indice_completacion", "indice_evento", "indice_vod"}
VARIABLES_CATEGORICAS = {"estructura_overworld", "tipo_bastion_nether", "jugador_tipo_rol", "jugador_pais", "variacion", "tipo_evento"}
VARIABLES_BOOLEANAS = {"partida_sin_completarse"}
VARIABLES_BINARIAS_RESULTADO = {"victoria_jugador_1"}
VARIABLES_CONTEXTO = {"temporada"}
UMBRAL_ALTA_AUSENCIA = 90.0

VARIABLES_NUMERICAS = {
    "partidas": ["tiempo_resultado_segundos", "posicion_partida_temporada", "posicion_partida_historia"],
    "partida_jugadores": ["jugador_elo", "jugador_posicion_ranking"],
    "seed_torres": ["altura_torre"],
    "cambios_elo": ["cambio_elo", "elo"],
    "completaciones": ["tiempo_completacion_ms"],
    "lineas_tiempo": ["tiempo_evento_ms"]
}

VARIABLES_CATEGORICAS_ANALISIS = {
    "partidas": ["estructura_overworld", "tipo_bastion_nether"],
    "jugadores": ["jugador_pais"],
    "partida_jugadores": ["jugador_tipo_rol", "jugador_pais"]
}
# Se elimina jugador_pais x jugador_elo porque generaba cientos de grupos
# estadisticos y no aportaba una lectura adecuada al reporte principal.
CONFIGURACION_AGRUPADA = [
    {"tabla": "partidas", "grupo": "estructura_overworld", "variable": "tiempo_resultado_segundos"},
    {"tabla": "partidas", "grupo": "tipo_bastion_nether", "variable": "tiempo_resultado_segundos"},
    {"tabla": "partida_jugadores", "grupo": "jugador_tipo_rol", "variable": "jugador_elo"},
    {"tabla": "partida_jugadores", "grupo": "jugador_tipo_rol", "variable": "jugador_posicion_ranking"},
    {"tabla": "seed_torres", "grupo": "indice_torre", "variable": "altura_torre"}
]

"""
████████████████████████████████████████████████████████████████████████████
█  FUNCIONES GENERALES                                                     █
████████████████████████████████████████████████████████████████████████████
"""
def imprimir_titulo(texto):
    print(f"\n{'=' * 70}\n{texto}\n{'=' * 70}")

def cargar_dataset(ruta, nombre):
    df = pd.read_csv(ruta)
    print(f"{nombre:25} {len(df):>10,} filas | {len(df.columns):>2} columnas")
    return df

def convertir_fechas(tablas):
    tablas["partidas"]["fecha_partida"] = pd.to_datetime(tablas["partidas"]["fecha_partida"], errors="coerce")
    tablas["vod"]["fecha_inicio_vod"] = pd.to_datetime(tablas["vod"]["fecha_inicio_vod"], errors="coerce")
    return tablas

def obtener_moda(serie):
    datos = serie.dropna()
    if datos.empty:
        return "Sin datos", 0
    frecuencias = datos.value_counts()
    frecuencia_maxima = frecuencias.iloc[0]
    if frecuencia_maxima <= 1:
        return "Sin moda unica", int(frecuencia_maxima)
    modas = frecuencias[frecuencias == frecuencia_maxima].index.tolist()
    return ", ".join(str(valor) for valor in modas), int(frecuencia_maxima)

def calcular_estadisticas(serie):
    datos = pd.to_numeric(serie,errors="coerce").dropna()
    if datos.empty:
        return {
            "conteo": 0,
            "sumatoria": np.nan,
            "minimo": np.nan,
            "maximo": np.nan,
            "media": np.nan,
            "moda": "Sin datos",
            "frecuencia_moda": 0,
            "curtosis": np.nan,
            "varianza": np.nan,
            "desviacion_estandar": np.nan
        }
    moda, frecuencia_moda = obtener_moda(datos)
    return {
        "conteo": int(datos.count()),
        "sumatoria": datos.sum(),
        "minimo": datos.min(),
        "maximo": datos.max(),
        "media": datos.mean(),
        "moda": moda,
        "frecuencia_moda": frecuencia_moda,
        "curtosis": datos.kurt(),
        "varianza": datos.var(),
        "desviacion_estandar": datos.std()
    }

def guardar_dataframe(df, ruta):
    df.to_csv(ruta, index=False, encoding="utf-8-sig")


"""
████████████████████████████████████████████████████████████████████████████
█  REGISTRO DE SALIDA EN CONSOLA Y ARCHIVO TXT                             █
████████████████████████████████████████████████████████████████████████████
"""
class SalidaDuplicada:
    def __init__(self, salida_original, archivo):
        self.salida_original = salida_original
        self.archivo = archivo

    def write(self, texto):
        self.salida_original.write(texto)
        self.archivo.write(texto)
        self.salida_original.flush()
        self.archivo.flush()

    def flush(self):
        self.salida_original.flush()
        self.archivo.flush()

@contextmanager
def registrar_salida(ruta):
    archivo = open(ruta, "w", encoding="utf-8")
    salida_original = sys.stdout
    sys.stdout = SalidaDuplicada(salida_original, archivo)
    try:
        yield
    finally:
        sys.stdout = salida_original
        archivo.close()


"""
████████████████████████████████████████████████████████████████████████████
█  FUNCIONES DE AUXILIARES                                                 █
████████████████████████████████████████████████████████████████████████████
"""
def clasificar_variable(columna, serie):
    if columna in VARIABLES_IDENTIFICADOR: return "Identificador", "Conteo"
    if columna in VARIABLES_INDICE: return "Indice", "Conteo"
    if columna in VARIABLES_CATEGORICAS: return "Categorica", "Conteo, Moda"
    if columna in VARIABLES_BOOLEANAS: return "Booleana", "Conteo, Moda"
    if columna in VARIABLES_BINARIAS_RESULTADO: return "Binaria / Resultado", "Conteo, Moda, Sumatoria"
    if columna in VARIABLES_CONTEXTO: return "Contexto", "Conteo"
    if pd.api.types.is_datetime64_any_dtype(serie):
        return "Fecha", "Conteo, Minimo, Maximo"
    if pd.api.types.is_numeric_dtype(serie):
        return "Numerica", "Minimo, Maximo, Media, Moda, Conteo, Sumatoria, Curtosis, Varianza, Desviacion estandar"
    return "Texto", "Conteo, Moda"

def obtener_observacion_nulos(porcentaje):
    if porcentaje >= UMBRAL_ALTA_AUSENCIA:
        return "Alta ausencia: interpretar con precaucion"
    if porcentaje > 0:
        return "Presenta valores faltantes"
    return ""

def generar_inventario(tablas):
    imprimir_titulo("INVENTARIO Y CLASIFICACION DE VARIABLES")
    inventario = []

    for nombre, tabla in tablas.items():
        total_filas = len(tabla)
        nulos_totales = tabla.isna().sum()

        for columna in tabla.columns:
            serie = tabla[columna]
            nulos = int(nulos_totales[columna])
            porcentaje_nulos = (nulos / total_filas * 100) if total_filas > 0 else 0.0
            categoria, operaciones = clasificar_variable(columna, serie)
            inventario.append({
                "tabla": nombre,
                "variable": columna,
                "tipo_dato": str(serie.dtype),
                "categoria": categoria,
                "nulos": nulos,
                "porcentaje_nulos": porcentaje_nulos,
                "operaciones_aplicables": operaciones
            })
    df_inventario = pd.DataFrame(inventario)
    guardar_dataframe(df_inventario, SALIDA_INVENTARIO)
    print(df_inventario.to_string(index=False))
    return df_inventario

def mostrar_variables_alta_ausencia(df_inventario):
    imprimir_titulo("VARIABLES CON ALTA AUSENCIA")
    altas = df_inventario[df_inventario["porcentaje_nulos"] >= UMBRAL_ALTA_AUSENCIA]
    if altas.empty:
        print("No se encontraron variables con alta ausencia.")
    else:
        print(altas[["tabla", "variable", "nulos", "porcentaje_nulos"]].to_string(index=False))

"""
████████████████████████████████████████████████████████████████████████████
█  CARGAR DATASET                                                          █
████████████████████████████████████████████████████████████████████████████
"""
def cargar_tablas():
    imprimir_titulo("CARGANDO DATASETS FINALES")
    tablas = {
        "partidas": cargar_dataset(CSV_PARTIDAS, "partidas"),
        "jugadores": cargar_dataset(CSV_JUGADORES, "jugadores"),
        "partida_jugadores": cargar_dataset(CSV_PARTIDA_JUGADORES, "partida_jugadores"),
        "seed_torres": cargar_dataset(CSV_SEED_TORRES, "seed_torres"),
        "seed_variaciones": cargar_dataset(CSV_SEED_VARIACIONES, "seed_variaciones"),
        "cambios_elo": cargar_dataset(CSV_CAMBIOS_ELO, "cambios_elo"),
        "completaciones": cargar_dataset(CSV_COMPLETACIONES, "completaciones"),
        "lineas_tiempo": cargar_dataset(CSV_LINEAS_TIEMPO, "lineas_tiempo"),
        "vod": cargar_dataset(CSV_VOD, "vod")
    }
    return tablas
"""
████████████████████████████████████████████████████████████████████████████
█  MOSTRAR VARIABLES NUMERICAS SELECCIONADAS                               █
████████████████████████████████████████████████████████████████████████████
"""
def mostrar_variables_numericas(tablas):
    imprimir_titulo("VARIABLES NUMERICAS SELECCIONADAS")
    for nombre, columnas in VARIABLES_NUMERICAS.items():
        print(f"\n{nombre.upper()}")
        for columna in columnas:
            if columna in tablas[nombre].columns:
                print(f"  - {columna}")

"""
████████████████████████████████████████████████████████████████████████████
█  FUNCIONES ANALITICAS                                                    █
████████████████████████████████████████████████████████████████████████████
"""
def generar_estadistica_descriptiva(tablas):
    imprimir_titulo("ESTADISTICA DESCRIPTIVA NUMERICA")
    resultados_estadistica = []
    for nombre, columnas in VARIABLES_NUMERICAS.items():
        for columna in columnas:
            if columna not in tablas[nombre].columns: continue
            estadisticas = calcular_estadisticas(tablas[nombre][columna])
            resultados_estadistica.append({"tabla": nombre, "variable": columna, **estadisticas})

    df_estadisticas = pd.DataFrame(resultados_estadistica)
    guardar_dataframe(df_estadisticas, SALIDA_ESTADISTICAS)
    print(df_estadisticas.to_string(index=False))
    return df_estadisticas

def imprimir_frecuencias_agrupadas(frecuencias):
    grupos = {}
    faltantes = []
    for valor, cantidad in frecuencias.items():
        cantidad = int(cantidad)
        valor = str(valor)
        if valor == "VALOR_FALTANTE":
            faltantes.append(cantidad)
        else:
            if cantidad not in grupos:
                grupos[cantidad] = []
            grupos[cantidad].append(valor)
    if faltantes:
        print(f"  VALOR_FALTANTE: {faltantes[0]:,}")
    for cantidad in sorted(grupos, reverse=True):
        valores = ", ".join(sorted(grupos[cantidad]))
        print(f"  {cantidad:,}: {valores}")

def generar_frecuencias(tablas):
    imprimir_titulo("FRECUENCIAS DE VARIABLES CATEGORICAS")
    resultados_frecuencias = []
    for nombre, columnas in VARIABLES_CATEGORICAS_ANALISIS.items():
        for columna in columnas:
            if columna in tablas[nombre].columns: 
                serie = tablas[nombre][columna].astype("string").fillna("VALOR_FALTANTE")
                frecuencias = serie.value_counts(dropna=False)
                for valor, cantidad in frecuencias.items():
                    porcentaje = cantidad /len(serie) *100
                    resultados_frecuencias.append({"tabla": nombre, "variable": columna, "valor": valor, "conteo": int(cantidad), "porcentaje": porcentaje})

                moda, frecuencia_moda = obtener_moda(tablas[nombre][columna])
                print(f"\n{nombre} -> {columna}")
                if columna == "jugador_pais":
                    imprimir_frecuencias_agrupadas(frecuencias)
                    print("Nota: la moda se calcula excluyendo los valores faltantes (VALOR_FALTANTE).")
                    print(f"Moda (sin valores faltantes): {moda} (frecuencia: {frecuencia_moda:,})")
                else:
                    print(frecuencias.to_string())
                    print(f"Moda: {moda} (frecuencia: {frecuencia_moda:,})")
    df_frecuencias = pd.DataFrame(resultados_frecuencias)
    guardar_dataframe(df_frecuencias, SALIDA_FRECUENCIAS)
    return df_frecuencias

def analizar_resultados(tablas):
    imprimir_titulo("ANALISIS DEL RESULTADO DE LAS PARTIDAS")
    df_partidas = tablas["partidas"]
    victorias_jugador_1 = (df_partidas["victoria_jugador_1"] == 1).sum()
    victorias_jugador_2 = (df_partidas["victoria_jugador_1"] == 0).sum()
    sin_ganador = (df_partidas["victoria_jugador_1"].isna()).sum()
    partidas_completadas = (df_partidas["partida_sin_completarse"] == False).sum()
    partidas_sin_completar = (df_partidas["partida_sin_completarse"] == True).sum()

    print(f"Victorias jugador 1:       {victorias_jugador_1:,}")
    print(f"Victorias jugador 2:       {victorias_jugador_2:,}")
    print(f"Partidas sin ganador:      {sin_ganador:,}")
    print(f"Partidas completadas:      {partidas_completadas:,}")
    print(f"Partidas sin completar:    {partidas_sin_completar:,}")
    print(f"Sumatoria de victorias J1: {df_partidas['victoria_jugador_1'].sum():,}")

def generar_metricas_agrupadas(tablas):
    imprimir_titulo("METRICAS AGRUPADAS")
    resultados_agrupados = []
    for configuracion in CONFIGURACION_AGRUPADA:
        nombre = configuracion["tabla"]
        columna_grupo = configuracion["grupo"]
        columna_variable = configuracion["variable"]
        tabla = tablas[nombre]

        if columna_grupo in tabla.columns and columna_variable in tabla.columns:
            grupos = tabla.groupby(columna_grupo, dropna=False)
            for valor_grupo, grupo in grupos:
                estadisticas = calcular_estadisticas(grupo[columna_variable])
                resultados_agrupados.append({"tabla": nombre, "variable_agrupadora": columna_grupo, "grupo": valor_grupo, "variable_analizada": columna_variable, **estadisticas})

    df_agrupadas = pd.DataFrame(resultados_agrupados)
    guardar_dataframe(df_agrupadas, SALIDA_AGRUPADAS)
    print(df_agrupadas.to_string(index=False))
    return df_agrupadas

def analizar_partidas_pais(tablas):
    imprimir_titulo("PARTIDAS POR PAIS")
    participaciones_pais = tablas["partida_jugadores"].groupby("jugador_pais", dropna=False)["id_partida"].nunique().reset_index(name="partidas")
    participaciones_pais["jugador_pais"] = participaciones_pais["jugador_pais"].astype("string").fillna("VALOR_FALTANTE")
    participaciones_pais = participaciones_pais.sort_values("partidas", ascending=False).reset_index(drop=True)
    guardar_dataframe(participaciones_pais, SALIDA_PARTICIPACIONES)
    grupos = {}
    faltantes = []
    for _, fila in participaciones_pais.iterrows():
        pais = fila["jugador_pais"]
        cantidad = int(fila["partidas"])
        if pais == "VALOR_FALTANTE":
            faltantes.append(cantidad)
        else:
            if cantidad not in grupos:
                grupos[cantidad] = []
            grupos[cantidad].append(str(pais))
    print("Paises agrupados por cantidad de partidas:")
    if faltantes:
        print(f"  VALOR_FALTANTE: {faltantes[0]:,}")
    for cantidad in sorted(grupos, reverse=True):
        valores = ", ".join(sorted(grupos[cantidad]))
        print(f"  {cantidad:,}: {valores}")
    return participaciones_pais

def analizar_temporal(tablas):
    imprimir_titulo("ANALISIS TEMPORAL")
    df_partidas = tablas["partidas"]
    df_partidas["fecha_dia"] = df_partidas["fecha_partida"].dt.floor("D")
    analisis_temporal = df_partidas.groupby("fecha_dia", dropna=False).agg(
        partidas=("id_partida", "count"),
        tiempo_promedio_segundos=("tiempo_resultado_segundos", "mean"),
        tiempo_minimo_segundos=("tiempo_resultado_segundos", "min"),
        tiempo_maximo_segundos=("tiempo_resultado_segundos", "max")
    ).reset_index()
    analisis_temporal["porcentaje_partidas"] = analisis_temporal["partidas"] / len(df_partidas) * 100
    guardar_dataframe(analisis_temporal, SALIDA_TEMPORAL)
    print(analisis_temporal.to_string(index=False))
    print(f"\nFecha minima: {df_partidas['fecha_partida'].min()}")
    print(f"Fecha maxima: {df_partidas['fecha_partida'].max()}")
    print(f"Dias con registros: {df_partidas['fecha_dia'].nunique():,}")
    return analisis_temporal


"""
████████████████████████████████████████████████████████████████████████████
█  ENTIDADES Y RELACIONES EXISTENTES EN EL DATASET                         █
████████████████████████████████████████████████████████████████████████████
"""
def generar_relaciones():
    imprimir_titulo("ENTIDADES Y RELACIONES")
    relaciones = [
        {"entidad_origen": "jugadores", "clave_origen": "jugador_uuid", "relacion": "1:N", "entidad_destino": "partida_jugadores", "clave_destino": "jugador_uuid", "descripcion": "Un jugador puede participar en muchas partidas."},
        {"entidad_origen": "partidas", "clave_origen": "id_partida", "relacion": "1:N", "entidad_destino": "partida_jugadores", "clave_destino": "id_partida", "descripcion": "Una partida tiene dos participaciones de jugadores."},
        {"entidad_origen": "partidas", "clave_origen": "id_partida", "relacion": "1:N", "entidad_destino": "seed_torres", "clave_destino": "id_partida", "descripcion": "Cada partida contiene cuatro alturas de torres."},
        {"entidad_origen": "partidas", "clave_origen": "id_partida", "relacion": "1:N", "entidad_destino": "seed_variaciones", "clave_destino": "id_partida", "descripcion": "Una partida puede contener varias variaciones de semilla."},
        {"entidad_origen": "partidas", "clave_origen": "id_partida", "relacion": "1:N", "entidad_destino": "cambios_elo", "clave_destino": "id_partida", "descripcion": "Cada partida registra los cambios de ELO asociados."},
        {"entidad_origen": "partidas", "clave_origen": "id_partida", "relacion": "1:N", "entidad_destino": "completaciones", "clave_destino": "id_partida", "descripcion": "Una partida puede tener cero, una o dos completaciones."},
        {"entidad_origen": "partidas","clave_origen": "id_partida", "relacion": "1:N", "entidad_destino": "lineas_tiempo", "clave_destino": "id_partida", "descripcion": "Una partida puede contener muchos eventos temporales."},
        {"entidad_origen": "partidas", "clave_origen": "id_partida", "relacion": "1:N", "entidad_destino": "vod", "clave_destino": "id_partida", "descripcion": "Una partida puede tener registros de VOD."}
    ]
    df_relaciones = pd.DataFrame(relaciones)
    guardar_dataframe(df_relaciones, SALIDA_RELACIONES)
    print(df_relaciones.to_string(index=False))
    return df_relaciones

def validar_relaciones(tablas):
    imprimir_titulo("VALIDACION DE RELACIONES")
    ids_partidas = set(tablas["partidas"]["id_partida"].dropna())
    uuid_jugadores = set(tablas["jugadores"]["jugador_uuid"].dropna())
    tablas_partida = ["partida_jugadores", "seed_torres", "seed_variaciones", "cambios_elo", "completaciones", "lineas_tiempo", "vod"]
    tablas_jugador = ["partida_jugadores", "cambios_elo", "completaciones", "lineas_tiempo"]

    for nombre in tablas_partida:
        ids_relacion = set(tablas[nombre]["id_partida"].dropna())
        print(f"{nombre}: relaciones con partida inexistente: {len(ids_relacion - ids_partidas)}")

    for nombre in tablas_jugador:
        uuid_relacion = set(tablas[nombre]["jugador_uuid"].dropna())
        print(f"{nombre}: jugadores inexistentes: {len(uuid_relacion - uuid_jugadores)}")
        
    participaciones_por_partida = tablas["partida_jugadores"]["id_partida"].value_counts().reindex(ids_partidas, fill_value=0)
    partidas_dos_jugadores = (participaciones_por_partida == 2).sum()
    partidas_no_dos_jugadores = (participaciones_por_partida != 2).sum()

    torres_por_partida = tablas["seed_torres"]["id_partida"].value_counts().reindex(ids_partidas, fill_value=0)
    partidas_cuatro_torres = (torres_por_partida == 4).sum()
    partidas_no_cuatro_torres = (torres_por_partida != 4).sum()

    cambios_elo_por_partida = tablas["cambios_elo"]["id_partida"].value_counts().reindex(ids_partidas, fill_value=0)
    partidas_dos_cambios_elo = (cambios_elo_por_partida == 2).sum()
    partidas_no_dos_cambios_elo = (cambios_elo_por_partida != 2).sum()

    completaciones_por_partida = tablas["completaciones"]["id_partida"].value_counts().reindex(ids_partidas, fill_value=0)
    partidas_cero_completaciones = (completaciones_por_partida == 0).sum()
    partidas_una_completacion = (completaciones_por_partida == 1).sum()
    partidas_dos_completaciones = (completaciones_por_partida == 2).sum()
    partidas_mas_de_dos_completaciones = (completaciones_por_partida > 2).sum()

    uuid_relacion = set(tablas["partida_jugadores"]["jugador_uuid"].dropna())
    jugadores_sin_participacion = uuid_jugadores - uuid_relacion

    print(f"Partidas con exactamente 2 jugadores: {partidas_dos_jugadores:,}")
    print(f"Partidas con cantidad distinta de 2 jugadores: {partidas_no_dos_jugadores:,}")
    print(f"Partidas con exactamente 4 torres: {partidas_cuatro_torres:,}")
    print(f"Partidas con cantidad distinta de 4 torres: {partidas_no_cuatro_torres:,}")
    print(f"Partidas con exactamente 2 cambios de ELO: {partidas_dos_cambios_elo:,}")
    print(f"Partidas con cantidad distinta de 2 cambios de ELO: {partidas_no_dos_cambios_elo:,}")
    print(f"Partidas con 0 completaciones: {partidas_cero_completaciones:,}")
    print(f"Partidas con 1 completacion: {partidas_una_completacion:,}")
    print(f"Partidas con 2 completaciones: {partidas_dos_completaciones:,}")
    print(f"Partidas con mas de 2 completaciones: {partidas_mas_de_dos_completaciones:,}")
    print(f"Jugadores sin participacion: {len(jugadores_sin_participacion):,}")

"""
████████████████████████████████████████████████████████████████████████████
█  DIBUJAR ER                                                              █
████████████████████████████████████████████████████████████████████████████
"""
def dibujar_entidad(ax, x, y, ancho, alto, nombre, columnas):
    caja = FancyBboxPatch((x, y), ancho, alto, boxstyle="round,pad=0.05", linewidth=1.5, facecolor="#DCEAF7", edgecolor="#1F4E79", zorder=3)
    ax.add_patch(caja)
    ax.text(x + ancho / 2, y + alto - 0.23, nombre.upper(), ha="center", va="center", fontsize=11, fontweight="bold", color="#163A5F", zorder=4)
    ax.plot([x, x + ancho], [y + alto - 0.43, y + alto - 0.43], linewidth=0.8, color="#7A9AB5", zorder=4)
    for indice, columna in enumerate(columnas):
        ax.text(x + 0.16, y + alto - 0.68 - (indice * 0.21), columna, ha="left", va="top", fontsize=8.5, color="#111827", zorder=4)

def obtener_posicion_cardinalidad(p1, p2, inicio=True):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    if abs(dx) >= abs(dy):
        if inicio:
            return p1[0] + (0.12 if dx >= 0 else -0.12), p1[1] + 0.18
        return p1[0] + (0.12 if dx <= 0 else -0.12), p1[1] + 0.18
    if inicio:
        return p1[0] + 0.18, p1[1] + (0.12 if dy >= 0 else -0.12)
    return p1[0] + 0.18, p1[1] + (0.12 if dy <= 0 else -0.12)

def dibujar_relacion_ortogonal(ax, puntos, cardinalidad_inicio, cardinalidad_fin, texto_cardinalidad):
    xs, ys = [p[0] for p in puntos], [p[1] for p in puntos]
    ax.plot(xs, ys, linewidth=1.5, color="#4B5563", zorder=1)
    flecha = FancyArrowPatch(puntos[-2], puntos[-1], arrowstyle="-|>", mutation_scale=14, linewidth=1.5, color="#4B5563", zorder=2)
    ax.add_patch(flecha)
    pos_inicio = obtener_posicion_cardinalidad(puntos[0], puntos[1], True)
    pos_final = obtener_posicion_cardinalidad(puntos[-1], puntos[-2], False)
    estilo_texto = {"fontsize": 9, "fontweight": "bold", "ha": "center", "va": "center", "bbox": {"boxstyle": "round,pad=0.16", "facecolor": "white", "edgecolor": "#9CA3AF", "linewidth": 0.8}, "zorder": 5,}
    ax.text(pos_inicio[0], pos_inicio[1], cardinalidad_inicio, **estilo_texto)
    ax.text(pos_final[0], pos_final[1], cardinalidad_fin, **estilo_texto)
    punto_medio = len(puntos) // 2
    if len(puntos) % 2 == 0:
        x_medio = (puntos[punto_medio - 1][0] + puntos[punto_medio][0]) / 2
        y_medio = (puntos[punto_medio - 1][1] + puntos[punto_medio][1]) / 2
    else:
        x_medio, y_medio = puntos[punto_medio][0], puntos[punto_medio][1]
    ax.text(x_medio, y_medio + 0.22, texto_cardinalidad, fontsize=8.5, fontweight="bold", ha="center", va="center", bbox={"boxstyle": "round,pad=0.18", "facecolor": "white", "edgecolor": "#6B7280", "linewidth": 0.8}, zorder=5,)

def generar_diagrama():
    imprimir_titulo("GENERANDO DIAGRAMA DE ENTIDADES Y RELACIONES")
    fig, ax = plt.subplots(figsize=(16, 11))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 11)
    ax.axis("off")
    ancho = 4.2
    alto = 2.0
    entidades = {
        "jugadores": (0.6, 8.25, ["PK  jugador_uuid", "     jugador_nombre", "     jugador_pais"]),
        "partida_jugadores": (5.9, 8.25, ["PK/FK  id_partida", "PK      indice_jugador", "FK      jugador_uuid", "        jugador_elo", "        jugador_posicion_ranking"]),
        "vod": (11.2, 8.25, ["PK/FK  id_partida", "PK      indice_vod", "        vod_uuid", "        vod_url", "        fecha_inicio_vod"]),
        "seed_torres": (0.6, 4.55, ["PK/FK  id_partida", "PK      indice_torre", "        altura_torre"]),
        "partidas": (5.9, 4.35, ["PK  id_partida", "    uuid_seed", "    estructura_overworld", "    tipo_bastion_nether", "    uuid_ganador", "    tiempo_resultado_segundos", "    fecha_partida"]),
        "lineas_tiempo": (11.2, 4.55, ["PK/FK  id_partida", "PK      indice_evento", "FK      jugador_uuid", "        tiempo_evento_ms", "        tipo_evento"]),
        "seed_variaciones": (0.6, 0.75, ["PK/FK  id_partida", "PK      indice_variacion", "        variacion"]),
        "cambios_elo": (5.9, 0.75, ["PK/FK  id_partida", "PK      indice_cambio", "FK      jugador_uuid", "        cambio_elo", "        elo"]),
        "completaciones": (11.2, 0.75, ["PK/FK  id_partida", "PK      indice_completacion", "FK      jugador_uuid", "        tiempo_completacion_ms"]),
    }
    for nombre, (x, y, columnas) in entidades.items():
        altura_entidad = 2.25 if nombre == "partidas" else alto
        dibujar_entidad(ax, x, y, ancho, altura_entidad, nombre, columnas)

    """
    Relaciones:
    jugadores 1:N partida_jugadores
    partidas 1:N partida_jugadores
    partidas 1:N seed_torres
    partidas 1:N seed_variaciones
    partidas 1:N cambios_elo
    partidas 1:N completaciones
    partidas 1:N lineas_tiempo
    partidas 1:N vod
    """
    dibujar_relacion_ortogonal(ax, [(4.8, 9.25), (5.9, 9.25)], "1", "N", "1:N / variable")
    dibujar_relacion_ortogonal(ax, [(8.0, 6.60), (8.0, 8.25)], "1", "N", "1:N / 1:2")
    dibujar_relacion_ortogonal(ax, [(5.9, 5.50), (4.8, 5.50)], "1", "N", "1:N / 1:4")
    dibujar_relacion_ortogonal(ax, [(10.1, 5.50), (11.2, 5.50)], "1", "N", "1:N / variable")
    dibujar_relacion_ortogonal(ax, [(6.45, 4.35), (6.45, 3.75), (4.8, 3.75), (4.8, 2.75)], "1", "N", "1:N / 1:2")
    dibujar_relacion_ortogonal(ax, [(8.0, 4.35), (8.0, 2.75)], "1", "N", "1:N / 0:2")
    dibujar_relacion_ortogonal(ax, [(9.55, 4.35), (9.55, 3.75), (12.4, 3.75), (12.4, 2.75)], "1", "N", "1:N / variable")
    dibujar_relacion_ortogonal(ax, [(9.55, 6.60), (9.55, 7.35), (13.3, 7.35), (13.3, 8.25)], "1", "N", "1:N / variable")
    ax.text(8.0, 0.20, "Leyenda: PK = clave primaria | FK = clave foranea | 1:N = una entidad en origen puede relacionarse con muchas en destino", ha="center", va="center", fontsize=9, color="#374151")
    ax.set_title("Modelo de entidades y relaciones - MCSR Ranked Temporada 10", fontsize=15, pad=18, fontweight="bold")
    plt.savefig(SALIDA_DIAGRAMA, dpi=220, bbox_inches="tight")
    plt.close()
    print(f"Diagrama guardado en:\n{SALIDA_DIAGRAMA}")

"""
████████████████████████████████████████████████████████████████████████████
█  RESUMEN                                                                 █
████████████████████████████████████████████████████████████████████████████
"""
def mostrar_resumen(tablas, df_inventario, df_estadisticas, df_agrupadas):
    imprimir_titulo("RESUMEN DE LA ACT 2")
    print(f"Partidas analizadas: {len(tablas['partidas']):,}")
    print(f"Jugadores analizados: {len(tablas['jugadores']):,}")
    print(f"Participaciones jugador-partida: {len(tablas['partida_jugadores']):,}")
    print(f"Variables registradas en inventario: {len(df_inventario):,}")
    print(f"Variables numericas analizadas: {len(df_estadisticas):,}")
    print(f"Grupos estadisticos generados: {len(df_agrupadas):,}")
    print(f"\nResultados guardados en: {RESULTADOS_DIR}")

"""
████████████████████████████████████████████████████████████████████████████
█  MAIN                                                                    █
████████████████████████████████████████████████████████████████████████████
"""
def ejecutar_act2():
    with registrar_salida(SALIDA_REPORTE):
        imprimir_titulo("ACT 2 - ESTADISTICA DESCRIPTIVA")

        tablas = cargar_tablas()
        tablas = convertir_fechas(tablas)

        df_inventario = generar_inventario(tablas)
        mostrar_variables_alta_ausencia(df_inventario)

        mostrar_variables_numericas(tablas)
        df_estadisticas = generar_estadistica_descriptiva(tablas)
        generar_frecuencias(tablas)
        analizar_resultados(tablas)

        df_agrupadas = generar_metricas_agrupadas(tablas)
        analizar_partidas_pais(tablas)
        analizar_temporal(tablas)

        generar_relaciones()
        validar_relaciones(tablas)
        generar_diagrama()

        mostrar_resumen(tablas, df_inventario, df_estadisticas, df_agrupadas)

        imprimir_titulo("ACT 2 COMPLETADA")

if __name__ == "__main__":
    ejecutar_act2()