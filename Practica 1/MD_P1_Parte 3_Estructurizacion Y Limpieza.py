"""
████████████████████████████████████████████████████████████████████████████
█  PROYECTO: MCSR RANKED - TEMPORADA 10                                    █
█  PROCESAMIENTO, REESTRUCTURACION Y LIMPIEZA DE DATOS                     █
████████████████████████████████████████████████████████████████████████████

------------------------->
DESCRIPCION GENERAL 
------------------------->
El script que se presenta a continuacion es la culminacion de varias
semanas de trabajo y rediseño arduo. Este realiza el procesamiento
de una muestra de 50,000 partidas clasificatorioas de MCSR Ranked 
de la temporada 10. Este procesado se dividio en dos 
etapas de programacion:

    1.- La reestructuracion de los datos brutos
    2.- La limpieza y validacion de los datos preprocesados

La finalidad total del codigo radica en transformar los datos que se
obtuvieron de la API de MSCR Ranked en un conjunto de tablas 
organizadas, relacionadas y preparadas para un posterior analisis 
estadistico.

------------------------->
DATOS DE ENTRADA
------------------------->
Los datos necesarios para el funcionamiento del programa proviene de los
archivos generados durante la etapa de extraccion de datos, mas 
especificamente de la ejecucion de las dos anteriores partes:
    - mcsr_ranked_season_10.csv
    - mcsr_ranked_season_10_aux.csv

El primer archivo contiene la informacion principal de las partidas, 
mientra el segundo contiene la informacion adicional asociada a esas
partidas.

------------------------->
ETAPA - 1
------------------------->
Esta tiene como finalidad reorganizar la informacion para evitar que 
diferentes tipos de datos permanezcan mezclados en una misma tabla.

A partir del dataset de mcsr_ranked_season_10 se separo la informacion
en tres tablas principales: partidas, jugadores y partida_jugadores

    - partidas: Contiene la informacion correspondiente a cada partida
    - jugadores: Lista de jugadores presentes identificadsos por su 
        UUID
    - partida_jugadores: La relacion entre cada partida y sus dos 
        jugadores, almacenando informacion especifica de su 
        participacion.

Asi mismo, del dataset auxiliar tambien se construyen tablas adicionales
como lo pueden ser:
    - seed_variaciones
    - cambios_elo
    - completaciones
    - lineas_tiempo
    - vod

-> ¿Por que una reestructuracion?
    Esto se hizo principalmente para reducir la redundancia y conservar 
    relaciones claras entre las entidades. Dado que un jugador podria 
    participar en muchas partidas sus datos podrian repetirse, asi mismo
    los datos como el elo dentro de la partida deben mantenerse en una 
    relacion independiente que solo se de entre el jugador y la partida.

-> Eliminacion de columnas
    Esta severa decision se llevo a cabo dado que se observo reiteradamente
    que estas columnas no aportaban un valor estadisco claro, o directamente
    no aportaban nada en si. Es decir, eran columnas con un solo valor 
    irrelevante o con un valor nulo.

------------------------->
ETAPA - 2
------------------------->
En esta etapa se comprobaron la calidad y consistencia de los datos alojados 
dentro de las tablas reestructuradas.
En particular se realizaron validaciones de:
    - duplicados exactos
    - identificadores nulos
    - rangos numéricos
    - temporadas
    - tiempos de partida
    - posiciones de ranking
    - fechas
    - formato de países
    - UUID de jugadores
    - cantidad de jugadores por partida
    - relaciones entre partidas y jugadores
    - relaciones entre partidas y tablas auxiliares
    - consistencia del ganador de cada partida
    - cardinalidad esperada de registros auxiliares
    - valores faltantes
    - tipos de datos

-> ¿Qué paso con el tratamiento a valor faltantes?
    Un valor faltante directamente no se elimina, ya que este representa una 
    ausencia de informacion valida y no un error, por lo tanto se contabilizan y 
    se conservan.

-> Tratamiento de valores atipicos
    Estos directamente no se eliminan, ya que se consideran eventos poco comunes o
    casos especiales, por lo que deben mantenerse para preservar la informacion.
    Un ejemplo de este tipo de valores serian las partidas con un tiempo de 
    resultado igual a 0.

-> Integridad
    Una vez realizada la limpieza individual de cada tabla, tambien se proceden
    a confirmar las relaciones entre ellas. Por ejemplo, se comprueba la 
    integridad con la relacion de id_partida y jugador_uuid

------------------------->
RESULTADO 
------------------------->
Al realizar el proceso deben existir dos estods claramente diferenciables:
    -TO_BE_CLEANED
        Contiene las tablas depues de su reestructuracion
    
    -FINAL
        Ya contiene las tablas despues de completar todo este procesados
    
    Asi mismo, se genera un reporte de limpieza con metricas del proceso.
"""


"""
████████████████████████████████████████████████████████████████████████████
█  LIBRERIAS                                                               █
████████████████████████████████████████████████████████████████████████████
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys
from contextlib import contextmanager


"""
████████████████████████████████████████████████████████████████████████████
█  CONDICIONES INICIALES                                                   █
████████████████████████████████████████████████████████████████████████████
"""

BASE_DIR = Path("MCSR_Ranked")
PROCESSED_DIR = BASE_DIR / "processed"
DATA_DIR = BASE_DIR / "data"
TO_BE_CLEANED_DIR = DATA_DIR / "to_be_cleaned"
TO_BE_CLEANED_MAIN_DIR = TO_BE_CLEANED_DIR / "main"
TO_BE_CLEANED_AUX_DIR = TO_BE_CLEANED_DIR / "aux"
FINAL_DIR = DATA_DIR / "final"
FINAL_MAIN_DIR = FINAL_DIR / "main"
FINAL_AUX_DIR = FINAL_DIR / "aux"

# Crear directorios necesarios
DATA_DIR.mkdir(parents=True, exist_ok=True)
TO_BE_CLEANED_DIR.mkdir(parents=True, exist_ok=True)
TO_BE_CLEANED_MAIN_DIR.mkdir(parents=True, exist_ok=True)
TO_BE_CLEANED_AUX_DIR.mkdir(parents=True, exist_ok=True)
FINAL_DIR.mkdir(parents=True, exist_ok=True)
FINAL_MAIN_DIR.mkdir(parents=True, exist_ok=True)
FINAL_AUX_DIR.mkdir(parents=True, exist_ok=True)

"""
████████████████████████████████████████████████████████████████████████████
█  ARCHIVOS DE ENTRADA Y SALIDA                                            █
████████████████████████████████████████████████████████████████████████████
"""
CSV_PRINCIPAL = (PROCESSED_DIR / "mcsr_ranked_season_10.csv")
CSV_AUXILIAR = (PROCESSED_DIR / "mcsr_ranked_season_10_aux.csv")

CSV_PARTIDAS = TO_BE_CLEANED_MAIN_DIR / "estructurado_partidas.csv"
CSV_JUGADORES = TO_BE_CLEANED_MAIN_DIR / "estructurado_jugadores.csv"
CSV_PARTIDA_JUGADORES = TO_BE_CLEANED_MAIN_DIR / "estructurado_partida_jugadores.csv"
CSV_SEED_TORRES = TO_BE_CLEANED_AUX_DIR / "estructurado_seed_torres.csv"
CSV_SEED_VARIACIONES = TO_BE_CLEANED_AUX_DIR / "estructurado_seed_variaciones.csv"
CSV_CAMBIOS_ELO = TO_BE_CLEANED_AUX_DIR / "estructurado_cambios_elo.csv"
CSV_COMPLETACIONES = TO_BE_CLEANED_AUX_DIR / "estructurado_completaciones.csv"
CSV_LINEAS_TIEMPO = TO_BE_CLEANED_AUX_DIR / "estructurado_lineas_tiempo.csv"
CSV_VOD = TO_BE_CLEANED_AUX_DIR / "estructurado_vod.csv"

SALIDA_PARTIDAS = FINAL_MAIN_DIR / "partidas.csv"
SALIDA_JUGADORES = FINAL_MAIN_DIR / "jugadores.csv"
SALIDA_PARTIDA_JUGADORES = FINAL_MAIN_DIR / "partida_jugadores.csv"
SALIDA_SEED_TORRES = FINAL_AUX_DIR / "seed_torres.csv"
SALIDA_SEED_VARIACIONES = FINAL_AUX_DIR / "seed_variaciones.csv"
SALIDA_CAMBIOS_ELO = FINAL_AUX_DIR / "cambios_elo.csv"
SALIDA_COMPLETACIONES = FINAL_AUX_DIR / "completaciones.csv"
SALIDA_LINEAS_TIEMPO = FINAL_AUX_DIR / "lineas_tiempo.csv"
SALIDA_VOD = FINAL_AUX_DIR / "vod.csv"

REPORTE_PROCESAMIENTO = (FINAL_DIR / "reporte_procesamiento.txt")
REPORTE_LIMPIEZA = (FINAL_DIR /"reporte_limpieza.csv")

"""
████████████████████████████████████████████████████████████████████████████
█  FUNCIONES GENERALES                                                     █
████████████████████████████████████████████████████████████████████████████
"""
def imprimir_titulo(texto):
    print("=" * 70)
    print(texto)
    print("=" * 70)

def cargar_dataset(ruta, nombre):
    imprimir_titulo(f"CARGANDO DATASET {nombre}...")
    df = pd.read_csv(ruta)
    print(f"Filas cargadas: {len(df):,}")
    print(f"Columnas cargadas: {len(df.columns)}")

    return df.replace(r"^\s*$", pd.NA, regex=True)

def convertir_columnas_numericas(df, columnas, tipo="Int64"):
    columnas_validas = [col for col in columnas if col in df.columns]
    for col in columnas_validas:
        df[col] = (pd.to_numeric(df[col], errors="coerce").round().astype(tipo))
    return df

def procesar_tabla_auxiliar(df_aux, tipo_dato, renombrar, columnas_finales, columnas_numericas):
    df_filtrado = df_aux[df_aux["tipo_dato"] == tipo_dato].copy()
    df_filtrado = df_filtrado.rename(columns=renombrar)
    df_filtrado = df_filtrado[columnas_finales]
    return convertir_columnas_numericas(df_filtrado, columnas_numericas, "Int64")

"""
████████████████████████████████████████████████████████████████████████████
█  REGISTRO DE SALIDA                                                      █
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
█  ETAPA 1 - REESTRUCTURACION                                              █
████████████████████████████████████████████████████████████████████████████
"""
def reestructurar_datos():
    imprimir_titulo("ETAPA 1 - REESTRUCTURACION DE DATOS")
    df = cargar_dataset(CSV_PRINCIPAL, "PRINCIPAL")
    filas_originales = len(df)

    columnas_eliminar = [
        "type","category","gameMode","decayed","beginner","botSource","seedType","bastionType","tag","replayExist","date_readable"
    ]

    columnas_eliminar = [columna for columna in columnas_eliminar if columna in df.columns]
    df = df.drop(columns=columnas_eliminar)

    renombrar = {
        "id": "id_partida",
        "seed_id": "uuid_seed",
        "seed_overworld": "estructura_overworld",
        "seed_nether": "tipo_bastion_nether",
        "result_uuid": "uuid_ganador",
        "result_time": "tiempo_resultado_ms",
        "forfeited": "partida_sin_completarse",
        "rank_season": "posicion_partida_temporada",
        "rank_allTime": "posicion_partida_historia",
        "season": "temporada",
        "date": "fecha_partida",
        
        "player_1_uuid": "jugador_1_uuid",
        "player_1_nickname": "jugador_1_nombre",
        "player_1_roleType": "jugador_1_tipo_rol",
        "player_1_eloRate": "jugador_1_elo",
        "player_1_eloRank": "jugador_1_posicion_ranking",
        "player_1_country": "jugador_1_pais",
        
        "player_2_uuid": "jugador_2_uuid",
        "player_2_nickname": "jugador_2_nombre",
        "player_2_roleType": "jugador_2_tipo_rol",
        "player_2_eloRate": "jugador_2_elo",
        "player_2_eloRank": "jugador_2_posicion_ranking",
        "player_2_country": "jugador_2_pais"
    }
    df = df.rename(columns={ori: nue for ori, nue in renombrar.items() if ori in df.columns})

    if "tiempo_resultado_ms" in df.columns:
        df["tiempo_resultado_segundos"] = df["tiempo_resultado_ms"] / 1000
        df["tiempo_resultado_minutos"] = df["tiempo_resultado_ms"] / 60000

    if "uuid_ganador" in df.columns and "jugador_1_uuid" in df.columns and "jugador_2_uuid" in df.columns:
        df["victoria_jugador_1"] = pd.NA
        df.loc[df["uuid_ganador"] == df["jugador_1_uuid"], "victoria_jugador_1"] = 1
        df.loc[df["uuid_ganador"].notna() & (df["uuid_ganador"] == df["jugador_2_uuid"]), "victoria_jugador_1"] = 0
        df["victoria_jugador_1"] = df["victoria_jugador_1"].astype("Int64")

    df_partidas = df.drop(
        columns = [
            "jugador_1_uuid", "jugador_1_nombre", "jugador_1_tipo_rol", 
            "jugador_1_elo", "jugador_1_posicion_ranking", "jugador_1_pais",
            "jugador_2_uuid", "jugador_2_nombre", "jugador_2_tipo_rol", 
            "jugador_2_elo", "jugador_2_posicion_ranking", "jugador_2_pais"
        ], errors="ignore"
    ).copy()

    df_partidas = convertir_columnas_numericas(df_partidas, [
        "id_partida", "tiempo_resultado_ms", "posicion_partida_temporada", 
        "posicion_partida_historia", "temporada", "victoria_jugador_1"
    ], "Int64")

    df_partidas = convertir_columnas_numericas(df_partidas, [
        "tiempo_resultado_segundos", "tiempo_resultado_minutos"
    ], "Float64")

    if "partida_sin_completarse" in df_partidas.columns:
        df_partidas["partida_sin_completarse"] = df_partidas["partida_sin_completarse"].astype("boolean")

    if "fecha_partida" in df_partidas.columns:
        df_partidas["fecha_partida"] = pd.to_datetime(df_partidas["fecha_partida"], errors="coerce")

    orden_partidas = [
    "id_partida", "uuid_seed", "estructura_overworld", "tipo_bastion_nether", "uuid_ganador", "tiempo_resultado_ms", 
    "tiempo_resultado_segundos", "tiempo_resultado_minutos", "partida_sin_completarse", 
    "posicion_partida_temporada", "posicion_partida_historia", "temporada", "fecha_partida", "victoria_jugador_1"
]
    df_partidas = df_partidas[
        [col for col in orden_partidas if col in df_partidas.columns] + 
        [col for col in df_partidas.columns if col not in orden_partidas]
    ]

    def extraer_jugador(df,indice):
        df_jugador = df[
            ["id_partida", f"jugador_{indice}_uuid", f"jugador_{indice}_nombre", 
            f"jugador_{indice}_tipo_rol", f"jugador_{indice}_elo", 
            f"jugador_{indice}_posicion_ranking", f"jugador_{indice}_pais"]
        ].copy()
        df_jugador = df_jugador.rename(
            columns={
                f"jugador_{indice}_uuid": "jugador_uuid",
                f"jugador_{indice}_nombre": "jugador_nombre",
                f"jugador_{indice}_tipo_rol": "jugador_tipo_rol",
                f"jugador_{indice}_elo": "jugador_elo",
                f"jugador_{indice}_posicion_ranking": "jugador_posicion_ranking",
                f"jugador_{indice}_pais": "jugador_pais"
        })
        df_jugador["indice_jugador"] = indice - 1
        return df_jugador
        
    df_partida_jugadores = pd.concat([extraer_jugador(df, 1), extraer_jugador(df, 2)], ignore_index=True)
    df_partida_jugadores = df_partida_jugadores[[
        "id_partida", "indice_jugador", "jugador_uuid", "jugador_nombre",
        "jugador_tipo_rol", "jugador_elo", "jugador_posicion_ranking", "jugador_pais"
    ]]

    df_partida_jugadores = convertir_columnas_numericas(df_partida_jugadores, [
        "id_partida", "indice_jugador", "jugador_tipo_rol", "jugador_elo", "jugador_posicion_ranking"
    ], "Int64")

    df_jugadores = df_partida_jugadores[["jugador_uuid", "jugador_nombre", "jugador_pais"]].copy()
    df_jugadores = (df_jugadores.sort_values("jugador_uuid").drop_duplicates(subset="jugador_uuid",keep="first").reset_index(drop=True))


    df_aux = cargar_dataset(CSV_AUXILIAR, "AUXILIAR")

    df_torres = procesar_tabla_auxiliar(
        df_aux, "seed.endTowers",
        {"match_id": "id_partida", "indice": "indice_torre", "valor": "altura_torre"},
        ["id_partida", "indice_torre", "altura_torre"], ["id_partida", "indice_torre", "altura_torre"]
    )
    df_variaciones = procesar_tabla_auxiliar(
        df_aux, "seed.variations",
        {"match_id": "id_partida", "indice": "indice_variacion", "valor": "variacion"},
        ["id_partida", "indice_variacion", "variacion"], ["id_partida", "indice_variacion"]
    )
    df_cambios = procesar_tabla_auxiliar(
        df_aux, "changes",
        {"match_id": "id_partida", "indice": "indice_cambio", "player_uuid": "jugador_uuid", "change": "cambio_elo", "eloRate": "elo"},
        ["id_partida", "indice_cambio", "jugador_uuid", "cambio_elo", "elo"], ["id_partida", "indice_cambio", "cambio_elo", "elo"]
    )
    df_completaciones = procesar_tabla_auxiliar(
        df_aux, "completions",
        {"match_id": "id_partida", "indice": "indice_completacion", "player_uuid": "jugador_uuid", "time": "tiempo_completacion_ms"},
        ["id_partida", "indice_completacion", "jugador_uuid", "tiempo_completacion_ms"],
        ["id_partida", "indice_completacion", "tiempo_completacion_ms"]
    )
    df_timeline = procesar_tabla_auxiliar(
        df_aux, "timelines",
        {"match_id": "id_partida", "indice": "indice_evento", "player_uuid": "jugador_uuid", "time": "tiempo_evento_ms", "type": "tipo_evento"},
        ["id_partida", "indice_evento", "jugador_uuid", "tiempo_evento_ms", "tipo_evento"], ["id_partida", "indice_evento", "tiempo_evento_ms"]
    )
    df_vod = procesar_tabla_auxiliar(
        df_aux, "vod",
        {"match_id": "id_partida", "indice": "indice_vod", "uuid": "vod_uuid", "url": "vod_url", "startsAt": "fecha_inicio_vod"},
        ["id_partida", "indice_vod", "vod_uuid", "vod_url", "fecha_inicio_vod"], ["id_partida", "indice_vod"]
    )
    if not df_vod.empty and "fecha_inicio_vod" in df_vod.columns:
        df_vod["fecha_inicio_vod"] = pd.to_datetime(df_vod["fecha_inicio_vod"],errors="coerce")

    tipos_procesados = ["seed.endTowers", "seed.variations", "players", "changes", "completions", "timelines", "vod"]
    registros_no_procesados = df_aux[~df_aux["tipo_dato"].isin(tipos_procesados)].copy()

    ARCHIVOS_SALIDA = {
        "partidas": (df_partidas, CSV_PARTIDAS),
        "jugadores": (df_jugadores, CSV_JUGADORES),
        "partida_jugadores": (df_partida_jugadores, CSV_PARTIDA_JUGADORES),
        "seed_torres": (df_torres, CSV_SEED_TORRES),
        "seed_variaciones": (df_variaciones, CSV_SEED_VARIACIONES),
        "cambios_elo": (df_cambios, CSV_CAMBIOS_ELO),
        "completaciones": (df_completaciones, CSV_COMPLETACIONES),
        "lineas_tiempo": (df_timeline, CSV_LINEAS_TIEMPO),
        "vod": (df_vod, CSV_VOD)
    }
    imprimir_titulo("GUARDANDO TABLAS ESTRUCTURADAS")
    for nombre, (tabla, archivo) in ARCHIVOS_SALIDA.items():
        tabla.to_csv(archivo, index=False, encoding="utf-8-sig")
        print(f"{nombre:25} {len(tabla):>10,} filas | {len(tabla.columns):>2} columnas")

    imprimir_titulo("VALIDACIONES ESTRUCTURALES")
    print(f"Partidas originales: {filas_originales:,}")
    print(f"Partidas finales:    {len(df_partidas):,}")
    print(f"IDs de partida duplicados: {df_partidas['id_partida'].duplicated().sum():,}")

    partidas_con_dos_jugadores = df_partida_jugadores.groupby("id_partida").size()
    print(f"Partidas con exactamente 2 jugadores: {(partidas_con_dos_jugadores == 2).sum():,}")
    print(f"Partidas con cantidad distinta de 2 jugadores: {(partidas_con_dos_jugadores != 2).sum():,}")

    print(f"UUID de jugadores duplicados: {df_jugadores['jugador_uuid'].duplicated().sum():,}")

    ids_partidas = set(df_partidas["id_partida"].dropna())
    ids_partida_jugadores = set(df_partida_jugadores["id_partida"].dropna())
    ids_auxiliares = set(df_aux["match_id"].dropna())

    print(f"Relaciones partida-jugador sin partida principal: {len(ids_partida_jugadores - ids_partidas):,}")
    print(f"IDs auxiliares sin partida principal: {len(ids_auxiliares - ids_partidas):,}")
    print(f"Registros auxiliares no clasificados: {len(registros_no_procesados):,}")

    if not registros_no_procesados.empty:
        print("\nTipos no clasificados:")
        print(registros_no_procesados["tipo_dato"].value_counts(dropna=False).to_string())

    imprimir_titulo("REESTRUCTURACION COMPLETADA")


"""
████████████████████████████████████████████████████████████████████████████
█  ETAPA 2 - LIMPIEZA DE DATOS                                             █
████████████████████████████████████████████████████████████████████████████
"""


def limpiar_datos():
    imprimir_titulo("ETAPA 2 - LIMPIEZA DE DATOS")

    archivos_entrada = {
        "partidas": CSV_PARTIDAS,
        "jugadores": CSV_JUGADORES,
        "partida_jugadores": CSV_PARTIDA_JUGADORES,
        "seed_torres": CSV_SEED_TORRES,
        "seed_variaciones": CSV_SEED_VARIACIONES,
        "cambios_elo": CSV_CAMBIOS_ELO,
        "completaciones": CSV_COMPLETACIONES,
        "lineas_tiempo": CSV_LINEAS_TIEMPO,
        "vod": CSV_VOD
    }
    tablas = {}

    imprimir_titulo("CARGANDO DATOS ESTRUCTURADOS")

    for nombre, ruta in archivos_entrada.items():
        tablas[nombre] = pd.read_csv(ruta)
        tablas[nombre] = (tablas[nombre].replace(r"^\s*$", pd.NA, regex=True))
        print(f"{nombre:25} {len(tablas[nombre]):>10,} filas | {len(tablas[nombre].columns):>2} columnas")

    imprimir_titulo("NORMALIZACION DE TEXTO")

    for nombre, tabla in tablas.items():
        columnas_texto = tabla.select_dtypes(include=["object", "string"]).columns
        for columna in columnas_texto:
            tabla[columna] = (tabla[columna].astype("string").str.strip())
        tablas[nombre] = tabla
        print(f"{nombre:25} texto estandarizado")

    metricas = {
        nombre: {
            "filas_originales": len(df),
            "duplicados_exactos_eliminados": 0,
            "registros_invalidos_eliminados": 0,
            "registros_huerfanos_eliminados": 0,
            "filas_finales": 0,
            "valores_faltantes_conservados": 0
        }
        for nombre, df in tablas.items()
    }

    imprimir_titulo("CONVERSION DE TIPOS DE DATOS")

    columnas_int64 = {
        "partidas": ["id_partida", "tiempo_resultado_ms", "posicion_partida_temporada", "posicion_partida_historia", "temporada", "victoria_jugador_1"],
        "partida_jugadores": ["id_partida", "indice_jugador", "jugador_tipo_rol", "jugador_elo", "jugador_posicion_ranking"],
        "seed_torres": ["id_partida", "indice_torre", "altura_torre"],
        "seed_variaciones": ["id_partida", "indice_variacion"],
        "cambios_elo": ["id_partida", "indice_cambio", "cambio_elo", "elo"],
        "completaciones": ["id_partida", "indice_completacion", "tiempo_completacion_ms"],
        "lineas_tiempo": ["id_partida", "indice_evento", "tiempo_evento_ms"],
        "vod": ["id_partida", "indice_vod"]
    }
    for nombre, columnas in columnas_int64.items():
        for columna in columnas:
            if columna in tablas[nombre].columns:
                tablas[nombre][columna] = pd.to_numeric(tablas[nombre][columna], errors="coerce").round().astype("Int64")

    columnas_float64 = {"partidas": ["tiempo_resultado_segundos", "tiempo_resultado_minutos"]}
    for nombre, columnas in columnas_float64.items():
        for columna in columnas:
            if columna in tablas[nombre].columns:
                tablas[nombre][columna] = pd.to_numeric(tablas[nombre][columna], errors="coerce").astype("Float64")

    if "partida_sin_completarse" in tablas["partidas"].columns:
        valores_booleanos = {"true": True, "false": False, "1": True, "0": False}
        tablas["partidas"]["partida_sin_completarse"] = (
            tablas["partidas"]["partida_sin_completarse"].astype("string").str.strip().str.lower().map(valores_booleanos).astype("boolean")
        )

    if "fecha_partida" in tablas["partidas"].columns:
        tablas["partidas"]["fecha_partida"] = pd.to_datetime(tablas["partidas"]["fecha_partida"], errors="coerce")


    if "fecha_inicio_vod" in tablas["vod"].columns:
        tablas["vod"]["fecha_inicio_vod"] = pd.to_datetime(tablas["vod"]["fecha_inicio_vod"], errors="coerce")

    imprimir_titulo("ELIMINACION DE DUPLICADOS Y REGISTROS INVALIDOS")

    for nombre, tabla in tablas.items():
        filas_antes = len(tabla)
        
        tabla_valida = tabla.drop_duplicates().copy()
        duplicados = filas_antes - len(tabla_valida)
        metricas[nombre]["duplicados_exactos_eliminados"] += duplicados

        if "id_partida" in tabla_valida.columns:
            filas_antes_id = len(tabla_valida)
            tabla_valida = tabla_valida.dropna(subset=["id_partida"]).copy()
            invalidos_id = filas_antes_id - len(tabla_valida)
        else:
            invalidos_id = 0

        filas_antes_filtros = len(tabla_valida)

        if nombre == "partidas":
            tabla_valida = tabla_valida[tabla_valida["temporada"].eq(10) | tabla_valida["temporada"].isna()]
            tabla_valida = tabla_valida[(tabla_valida["tiempo_resultado_ms"] >= 0) | tabla_valida["tiempo_resultado_ms"].isna()]
            tabla_valida = tabla_valida[(tabla_valida["posicion_partida_temporada"] > 0) | tabla_valida["posicion_partida_temporada"].isna()]
            tabla_valida = tabla_valida[(tabla_valida["posicion_partida_historia"] > 0) | tabla_valida["posicion_partida_historia"].isna()]

        elif nombre == "jugadores":
            tabla_valida = tabla_valida.dropna(subset=["jugador_uuid"]).copy()

        elif nombre == "partida_jugadores":
            tabla_valida = tabla_valida[tabla_valida["indice_jugador"].isin([0, 1])]
            tabla_valida = tabla_valida[(tabla_valida["jugador_elo"] >= 0) | tabla_valida["jugador_elo"].isna()]
            tabla_valida = tabla_valida[(tabla_valida["jugador_posicion_ranking"] > 0) | tabla_valida["jugador_posicion_ranking"].isna()]
            tabla_valida = tabla_valida.dropna(subset=["jugador_uuid"]).copy()

        elif nombre == "seed_torres":
            tabla_valida = tabla_valida[(tabla_valida["indice_torre"] >= 0) & (tabla_valida["altura_torre"] >= 0)]

        elif nombre == "seed_variaciones":
            tabla_valida = tabla_valida[(tabla_valida["indice_variacion"] >= 0) & tabla_valida["variacion"].notna()]

        elif nombre == "cambios_elo":
            tabla_valida = tabla_valida[tabla_valida["indice_cambio"] >= 0]
            tabla_valida = tabla_valida.dropna(subset=["jugador_uuid"]).copy()
            tabla_valida = tabla_valida[(tabla_valida["elo"] >= 0) | tabla_valida["elo"].isna()]

        elif nombre == "completaciones":
            tabla_valida = tabla_valida[(tabla_valida["indice_completacion"] >= 0) & (tabla_valida["tiempo_completacion_ms"] >= 0)]
            tabla_valida = tabla_valida.dropna(subset=["jugador_uuid"]).copy()

        elif nombre == "lineas_tiempo":
            tabla_valida = tabla_valida[(tabla_valida["indice_evento"] >= 0) & (tabla_valida["tiempo_evento_ms"] >= 0)]
            tabla_valida = tabla_valida.dropna(subset=["jugador_uuid", "tipo_evento"]).copy()

        elif nombre == "vod":
            tabla_valida = tabla_valida[tabla_valida["indice_vod"] >= 0]

        invalidos_filtros = filas_antes_filtros - len(tabla_valida)
        invalidos = invalidos_id + invalidos_filtros
        metricas[nombre]["registros_invalidos_eliminados"] += invalidos
        
        tablas[nombre] = tabla_valida.reset_index(drop=True)
        print(f"{nombre:25} {duplicados:>6,} duplicados | {invalidos:>6,} inválidos eliminados")

    imprimir_titulo("VALIDACIONES ESPECIFICAS")
    df_partidas = tablas["partidas"]

    duplicados_id_partida = df_partidas["id_partida"].duplicated().sum()
    print(f"IDs de partida duplicados: {duplicados_id_partida:,}")

    temporadas_invalidas = (df_partidas["temporada"].notna() & (df_partidas["temporada"] != 10)).sum()
    print(f"Registros con temporada diferente a 10: {temporadas_invalidas:,}")

    tiempos_negativos = (df_partidas["tiempo_resultado_ms"].notna() & (df_partidas["tiempo_resultado_ms"] < 0)).sum()
    print(f"Tiempos negativos: {tiempos_negativos:,}")

    tiempos_cero = df_partidas["tiempo_resultado_ms"].eq(0).sum()
    print(f"Tiempos iguales a 0: {tiempos_cero:,}")

    casos_tiempo_cero = df_partidas[df_partidas["tiempo_resultado_ms"] == 0]
    if not casos_tiempo_cero.empty:
        tiempos_cero_sin_completacion = casos_tiempo_cero["partida_sin_completarse"].fillna(False).eq(False).sum()
        print(f"Tiempo = 0 pero partida_sin_completarse != True: {tiempos_cero_sin_completacion:,}")

    ranking_temporada_invalido = (df_partidas["posicion_partida_temporada"].notna() & (df_partidas["posicion_partida_temporada"] <= 0)).sum()
    ranking_historia_invalido = (df_partidas["posicion_partida_historia"].notna() & (df_partidas["posicion_partida_historia"] <= 0)).sum()
    print(f"Posiciones de temporada <= 0: {ranking_temporada_invalido:,}")
    print(f"Posiciones históricas <= 0: {ranking_historia_invalido:,}")

    fechas_invalidas = df_partidas["fecha_partida"].isna().sum()
    print(f"Fechas de partida nulas o inválidas: {fechas_invalidas:,}")
    print(f"Fecha mínima registrada: {df_partidas['fecha_partida'].min()}")
    print(f"Fecha máxima registrada: {df_partidas['fecha_partida'].max()}")

    df_jugadores = tablas["jugadores"]
    duplicados_uuid = df_jugadores["jugador_uuid"].duplicated().sum()
    print(f"\nUUID de jugadores duplicados: {duplicados_uuid:,}")

    patron_pais = r"^[A-Za-z]{2}$"
    paises_invalidos = df_jugadores["jugador_pais"].dropna().astype("string").str.fullmatch(patron_pais).eq(False).sum()
    print(f"Países con formato inválido: {paises_invalidos:,}")

    df_partida_jugadores = tablas["partida_jugadores"]
    elo_negativo = (df_partida_jugadores["jugador_elo"].notna() & (df_partida_jugadores["jugador_elo"] < 0)).sum()
    ranking_negativo = (df_partida_jugadores["jugador_posicion_ranking"].notna() & (df_partida_jugadores["jugador_posicion_ranking"] <= 0)).sum()
    print(f"\nElo negativo: {elo_negativo:,}")
    print(f"Ranking <= 0: {ranking_negativo:,}")

    conteo_jugadores = df_partida_jugadores.groupby("id_partida").size().reindex(set(df_partidas["id_partida"]), fill_value=0)
    print(f"Partidas con exactamente 2 jugadores: {(conteo_jugadores == 2).sum():,}")
    print(f"Partidas con cantidad distinta de 2 jugadores: {(conteo_jugadores != 2).sum():,}")

    indices_invalidos = (~df_partida_jugadores["indice_jugador"].isin([0, 1])).sum()
    print(f"Índices de jugador diferentes de 0/1: {indices_invalidos:,}")

    jugadores_repetidos = df_partida_jugadores.duplicated(subset=["id_partida", "jugador_uuid"]).sum()
    print(f"Mismo jugador repetido en una partida: {jugadores_repetidos:,}")

    posiciones_repetidas = df_partida_jugadores.duplicated(subset=["id_partida", "indice_jugador"]).sum()
    print(f"Posiciones de jugador duplicadas: {posiciones_repetidas:,}")

    imprimir_titulo("LIMPIEZA DE REGISTROS HUERFANOS")

    partidas_validas = set(tablas["partidas"]["id_partida"].dropna())
    jugadores_validos = set(tablas["jugadores"]["jugador_uuid"].dropna())

    df_pj = tablas["partida_jugadores"]


    filas_antes = len(df_pj)
    df_pj_valido = df_pj[(df_pj["id_partida"].isin(partidas_validas)) & (df_pj["jugador_uuid"].isin(jugadores_validos))].copy()
    huerfanos = filas_antes - len(df_pj_valido)
    metricas["partida_jugadores"]["registros_huerfanos_eliminados"] = huerfanos
    tablas["partida_jugadores"] = df_pj_valido
    print(f"{'partida_jugadores':25} {huerfanos:>6,} huérfanos eliminados.")

    auxiliares = ["seed_torres", "seed_variaciones", "cambios_elo", "completaciones", "lineas_tiempo", "vod"]


    for nombre in auxiliares:
        df_aux = tablas[nombre]
        filas_antes = len(df_aux)
        df_aux_valido = df_aux[df_aux["id_partida"].isin(partidas_validas)].copy()
        huerfanos = filas_antes - len(df_aux_valido)
        metricas[nombre]["registros_huerfanos_eliminados"] = huerfanos
        tablas[nombre] = df_aux_valido
        print(f"{nombre:25} {huerfanos:>6,} huérfanos eliminados.")

    for nombre in ["cambios_elo", "completaciones", "lineas_tiempo"]:
        df_aux = tablas[nombre]
        uuids_no_existentes = (~df_aux["jugador_uuid"].isin(jugadores_validos)).sum()
        print(f"UUID sin jugador principal en {nombre}: {uuids_no_existentes:,}")


    imprimir_titulo("RECONSTRUYENDO LOGICA DE VICTORIAS (VECTORIZADO)")

    df_partidas = tablas["partidas"]
    df_pj = tablas["partida_jugadores"]

    df_pj_pivot = df_pj.pivot(index="id_partida", columns="indice_jugador", values="jugador_uuid").rename(columns={0: "uuid_jugador_0", 1: "uuid_jugador_1"})
    df_partidas = df_partidas.merge(df_pj_pivot, on="id_partida", how="left")

    ganador_no_coincide = (df_partidas["uuid_ganador"].notna() & (df_partidas["uuid_ganador"] != df_partidas["uuid_jugador_0"]) & (df_partidas["uuid_ganador"] != df_partidas["uuid_jugador_1"])).sum()
    print(f"Ganadores que no coinciden con ningún jugador (anomalías reportadas): {ganador_no_coincide:,}")

    condiciones = [
        (df_partidas["uuid_ganador"].notna() & (df_partidas["uuid_ganador"] == df_partidas["uuid_jugador_0"])),
        (df_partidas["uuid_ganador"].notna() & (df_partidas["uuid_ganador"] == df_partidas["uuid_jugador_1"]))
    ]
    resultados = [1, 0]

    df_partidas["victoria_jugador_1"] = np.select(condiciones, resultados, default=np.nan)
    df_partidas["victoria_jugador_1"] = pd.to_numeric(df_partidas["victoria_jugador_1"], errors="coerce").astype("Int64")
    df_partidas = df_partidas.drop(columns=["uuid_jugador_0", "uuid_jugador_1"])
    tablas["partidas"] = df_partidas

    imprimir_titulo("VALIDACION DEL RESULTADO DE LAS PARTIDAS")

    df_partidas = tablas["partidas"]
    df_pj = tablas["partida_jugadores"]

    df_pj_validacion = df_pj.pivot(index="id_partida", columns="indice_jugador", values="jugador_uuid").rename(columns={0: "uuid_jugador_0", 1: "uuid_jugador_1"})
    df_validacion = df_partidas.merge(df_pj_validacion, on="id_partida", how="left")

    ganador_no_coincide = (df_validacion["uuid_ganador"].notna() & (df_validacion["uuid_ganador"] != df_validacion["uuid_jugador_0"]) & (df_validacion["uuid_ganador"] != df_validacion["uuid_jugador_1"])).sum()
    print(f"Ganadores que no coinciden con ningún jugador: {ganador_no_coincide:,}")

    victoria_inconsistente_1 = (df_validacion["uuid_ganador"].notna() & (df_validacion["uuid_ganador"] == df_validacion["uuid_jugador_0"]) & (df_validacion["victoria_jugador_1"] != 1)).sum()
    victoria_inconsistente_2 = (df_validacion["uuid_ganador"].notna() & (df_validacion["uuid_ganador"] == df_validacion["uuid_jugador_1"]) & (df_validacion["victoria_jugador_1"] != 0)).sum()
    print(f"Ganador jugador 0 pero victoria != 1: {victoria_inconsistente_1:,}")
    print(f"Ganador jugador 1 pero victoria != 0: {victoria_inconsistente_2:,}")

    victoria_sin_ganador = (df_validacion["uuid_ganador"].isna() & df_validacion["victoria_jugador_1"].notna()).sum()
    print(f"Victoria registrada sin ganador: {victoria_sin_ganador:,}")

    ganador_jugador_0 = (df_validacion["uuid_ganador"] == df_validacion["uuid_jugador_0"])
    ganador_jugador_1 = (df_validacion["uuid_ganador"] == df_validacion["uuid_jugador_1"])
    casos_con_ganador = df_validacion["uuid_ganador"].notna()

    print(f"Total ganó jugador 0: {(ganador_jugador_0 & casos_con_ganador).sum():,}")
    print(f"Total ganó jugador 1: {(ganador_jugador_1 & casos_con_ganador).sum():,}")
    print(f"Total sin ganador: {(~casos_con_ganador).sum():,}")

    imprimir_titulo("REPORTANDO ANOMALIAS DE CARDINALIDAD")
    partidas_validas = set(tablas["partidas"]["id_partida"].dropna())

    conteo_jugadores = tablas["partida_jugadores"].groupby("id_partida").size().reindex(partidas_validas, fill_value=0)
    print(f"Partidas sin exactamente 2 jugadores: {(conteo_jugadores != 2).sum():,}")

    conteo_torres = tablas["seed_torres"].groupby("id_partida").size().reindex(partidas_validas, fill_value=0)
    print(f"Partidas sin exactamente 4 torres: {(conteo_torres != 4).sum():,}")

    conteo_elo = tablas["cambios_elo"].groupby("id_partida").size().reindex(partidas_validas, fill_value=0)
    print(f"Partidas sin exactamente 2 cambios de ELO: {(conteo_elo != 2).sum():,}")

    conteo_completaciones = tablas["completaciones"].groupby("id_partida").size().reindex(partidas_validas, fill_value=0)
    print(f"Partidas con más de 2 completaciones: {(conteo_completaciones > 2).sum():,}")

    conteo_vods = tablas["vod"].groupby("id_partida").size().reindex(partidas_validas, fill_value=0)
    print(f"Partidas con más de 2 VODs registrados: {(conteo_vods > 2).sum():,}")

    imprimir_titulo("VALIDACION DE DATOS VOD")

    df_vod = tablas["vod"]

    if "vod_url" in df_vod.columns:
        urls_invalidas = (~df_vod["vod_url"].fillna("").astype("string").str.lower().str.startswith(("http://", "https://")) & df_vod["vod_url"].notna()).sum()
    else:
        urls_invalidas = 0
    print(f"URLs VOD con formato inválido: {urls_invalidas:,}")

    if "fecha_inicio_vod" in df_vod.columns:
        fechas_vod_invalidas = df_vod["fecha_inicio_vod"].isna().sum()
    else:
        fechas_vod_invalidas = 0
    print(f"Fechas de inicio VOD nulas o inválidas: {fechas_vod_invalidas:,}")

    imprimir_titulo("REVISION FINAL DE NULOS ")

    for nombre, tabla in tablas.items():
        total_nulos = int(tabla.isna().sum().sum())
        metricas[nombre]["filas_finales"] = len(tabla)
        metricas[nombre]["valores_faltantes_conservados"] = total_nulos
        print(f"{nombre:25} {total_nulos:>10,} valores faltantes")

    imprimir_titulo("TIPOS DE DATOS FINALES")

    for nombre, tabla in tablas.items():
        print(f"\n{nombre.upper()}")
        print(tabla.dtypes.to_string())

    imprimir_titulo("GUARDANDO TABLAS LIMPIAS")

    salidas = {
        "partidas": SALIDA_PARTIDAS,
        "jugadores": SALIDA_JUGADORES,
        "partida_jugadores": SALIDA_PARTIDA_JUGADORES,
        "seed_torres": SALIDA_SEED_TORRES,
        "seed_variaciones": SALIDA_SEED_VARIACIONES,
        "cambios_elo": SALIDA_CAMBIOS_ELO,
        "completaciones": SALIDA_COMPLETACIONES,
        "lineas_tiempo": SALIDA_LINEAS_TIEMPO,
        "vod": SALIDA_VOD
    }
    for nombre, tabla in tablas.items():
        tabla.to_csv(salidas[nombre], index=False, encoding="utf-8-sig")
        print(f"{nombre:25} {len(tabla):>10,} filas | {len(tabla.columns):>2} columnas")

    imprimir_titulo("REPORTE FINAL DE LIMPIEZA")

    df_reporte = pd.DataFrame.from_dict(metricas, orient="index").reset_index()
    df_reporte = df_reporte.rename(columns={"index": "tabla"})

    df_reporte["filas_eliminadas_total"] = (
        df_reporte["duplicados_exactos_eliminados"] +
        df_reporte["registros_invalidos_eliminados"] +
        df_reporte["registros_huerfanos_eliminados"]
    )
    print(df_reporte.to_string(index=False))

    total_filas_originales = df_reporte["filas_originales"].sum()
    total_duplicados = df_reporte["duplicados_exactos_eliminados"].sum()
    total_invalidos = df_reporte["registros_invalidos_eliminados"].sum()
    total_huerfanos = df_reporte["registros_huerfanos_eliminados"].sum()
    total_eliminadas = df_reporte["filas_eliminadas_total"].sum()
    total_filas_finales = df_reporte["filas_finales"].sum()
    total_nulos = df_reporte["valores_faltantes_conservados"].sum()

    print("\n" + "=" * 70)
    print("RESUMEN GENERAL")
    print("=" * 70)
    print(f"Filas originales totales:       {total_filas_originales:,}")
    print(f"Duplicados exactos eliminados:  {total_duplicados:,}")
    print(f"Registros inválidos eliminados: {total_invalidos:,}")
    print(f"Registros huérfanos eliminados: {total_huerfanos:,}")
    print(f"Filas eliminadas totales:       {total_eliminadas:,}")
    print(f"Filas finales listas:           {total_filas_finales:,}")
    print(f"Valores faltantes conservados:  {total_nulos:,}")

    df_reporte.to_csv(REPORTE_LIMPIEZA, index=False, encoding="utf-8-sig")
    print(f"\nReporte de limpieza guardado en:\n{REPORTE_LIMPIEZA}")
    imprimir_titulo("LIMPIEZA COMPLETADA CON ÉXITO")


"""
████████████████████████████████████████████████████████████████████████████
█  EJECUCION PRINCIPAL                                                     █
████████████████████████████████████████████████████████████████████████████
"""

if __name__ == "__main__":
    with registrar_salida(REPORTE_PROCESAMIENTO):
        # ETAPA 1
        reestructurar_datos()

        # PAUSA ENTRE ETAPAS
        print("\nLas tablas estructuradas fueron guardadas correctamente.")
        print("La salida de esta etapa tambien fue guardada en:")
        print(f"{REPORTE_PROCESAMIENTO}")
        input("\nPresiona ENTER para continuar con la limpieza...")

        # ETAPA 2
        limpiar_datos()

        # FINAL
        imprimir_titulo("PROCESAMIENTO COMPLETO")
        print(f"\nReporte completo: {REPORTE_PROCESAMIENTO}")
        print(f"Reporte de limpieza: {REPORTE_LIMPIEZA}")