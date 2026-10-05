
"""
████████████████████████████████████████████████████████████████████████████
█  VISUALIZACION DE DATOS - MCSR RANKED TEMPORADA 10                       █
████████████████████████████████████████████████████████████████████████████


------------------------------------------------>
DESCRIPCION GENERAL DE PROGRAMA
------------------------------------------------>

Utiliza los datasets finales de MCSR RANKED Temporada 10 obtenidos durante
la practica uno, prepara las variables necesarias para la visualizacion
y genera automaticamente diferentes tipos de graficas, donde en cada una 
de ellas representa una caracteristica distinta del conjunto de datos. Los
resultados obtenidos durante la ejecucion del programa se almacenan como 
archivos independientes dentro de la carpeta de resultados de la practica
tres.

------------------------------------------------>
DIAGRAMAS A REALIZAR
------------------------------------------------>
-> Diagrama de Pastel: Las distribuciones de las estructuras del overwold
-> Histograma: La distribucion del tiempo de resultado de las partidas
-> Diagrama de caja: La distribucion de ELO por tipo de rol
-> Diagrama de dispersion: La relacion entre el ELO y la posicion del ranking
-> Grafica de lineas: El comportamiento de la cantidad de partidas por dia
-> Diagrama de barras: La distribucion de bastiones del nether

------------------------------------------------>
JUSTIFICACION DE DECISIONES
------------------------------------------------>

->  Se utiliza los dataset finales obtenidos durante la practica 1, para 
    que de ese modo la actividad pueda construirse con la informacion
    estructurada y depurada del proyecto, sin modificar las practicas
    anteriores

-> Los valores faltantes no se eliminana del dataset. Cuando una grafica
    necesita una variable con valores no nulos, la explusion de 
    registros se realiza solo durante la preparacion de la visualizacion
    , evitando alterar datos originales

->  Las variables con un alto porcentaje de valores faltantes, como 
    posiciones historicas y de temporada, no se utilizaran como variables
    principales de visualizacion dentro de la practica, esto debido a que
    la informacion disponible es limitada.

->  Para la duracion de partidas en este caso se utilizara la columna que
    la representa en segundos; tiempo_resultado_segundos. Con la finalidad
    de no usar columnas que representen el mismo dato. Para facilitar la 
    lectura del histograma, los valores se convierten a minutos solamente
    durante la visualizacion

->  En la serie temporal se conservan el indice de fechas reales en el eje X.
    El formato visual lo simplifica a dia/mes, pero la infromacion temporal 
    original no se convierte a texto ni se sustitue por posiciones numericas 

->  Las categorias de estructura del Overworld y de Bastiones del Nether se 
    traducen al español unicamente para las etiquetas de las graficas, para 
    una mejor comprension. Los valores originales del dataset no se 
    modificaron

->  Los valores de tipo de rol (RoleType) se muestran como Rol 0, Rol 1, Rol 2
    y Rol 3. No se asignaron nombres adicionales a estos valores debido a que
    la documentacion disponibles del API define roleType com un valor entero
    sin proporcionar una equivalencia oficial para cada codigo

->  En la grafica de caja se expluyeron temporalmente los registros cuyo ELO
    es nulo, ya que el diagrama requiere valores numericos para calcular la 
    distribucion. Estos registros permanecen en el dataset y solamente se omiten
    de esta visualizacion

->  Las graficas seleccionadas permiten representar distribuciones, comparaciones,
    relaciones entre variables y cambios atraves del tiempo
"""
from pathlib import Path
import pandas as pd
import math
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MultipleLocator
from contextlib import contextmanager
import sys

BASE_DIR = Path("MCSR_Ranked")
FINAL_DIR = BASE_DIR / "data" / "final"
MAIN_DIR = FINAL_DIR / "main"

CSV_PARTIDAS = MAIN_DIR / "partidas.csv"
CSV_PARTIDA_JUGADORES = MAIN_DIR / "partida_jugadores.csv"

ACT3_DIR = BASE_DIR / "Act_3"
RESULTADOS_DIR = ACT3_DIR / "resultados"
RESULTADOS_DIR.mkdir(parents=True, exist_ok=True)

SALIDA_GRAFICA_01 = RESULTADOS_DIR / "grafica_01_estructura_overworld.png"
SALIDA_GRAFICA_02 = RESULTADOS_DIR / "grafica_02_tiempo_resultado.png"
SALIDA_GRAFICA_03 = RESULTADOS_DIR / "grafica_03_elo_por_rol.png"
SALIDA_GRAFICA_04 = RESULTADOS_DIR / "grafica_04_elo_vs_ranking.png"
SALIDA_GRAFICA_05 = RESULTADOS_DIR / "grafica_05_partidas_por_dia.png"
SALIDA_GRAFICA_06 = RESULTADOS_DIR / "grafica_06_bastiones_nether.png"
SALIDA_REPORTE = RESULTADOS_DIR / "reporte_act_3.txt"

ETIQUETAS_ESTRUCTURAS = {"VILLAGE": "Aldea", "DESERT_TEMPLE": "Templo del desierto", "SHIPWRECK": "Naufragio", "RUINED_PORTAL": "Portal en ruinas", "BURIED_TREASURE": "Tesoro enterrado"}
ETIQUETAS_BASTIONES = {"BRIDGE": "Puente", "STABLES": "Establos", "TREASURE": "Tesoro", "HOUSING": "Vivienda"}

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
    return tablas

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
█  CARGAR DATASET                                                          █
████████████████████████████████████████████████████████████████████████████
"""
def cargar_tablas():
    imprimir_titulo("CARGANDO DATASETS FINALES")
    tablas = {
        "partidas": cargar_dataset(CSV_PARTIDAS, "partidas"),
        "partida_jugadores": cargar_dataset(CSV_PARTIDA_JUGADORES, "partida_jugadores")
    }
    return tablas

"""
████████████████████████████████████████████████████████████████████████████
█  PREPARACION DE DATOS                                                    █
████████████████████████████████████████████████████████████████████████████
"""
def preparar_datos_graficas(tablas):
    imprimir_titulo("PREPARANDO DATOS PARA VISUALIZACION")
    tablas = convertir_fechas(tablas)
    df_partidas = tablas["partidas"]
    df_partida_jugadores = tablas["partida_jugadores"]
    datos = {
        "estructura_overworld": (df_partidas["estructura_overworld"].dropna().value_counts()),
        "tiempo_resultado": (df_partidas["tiempo_resultado_segundos"].dropna()),
        "elo_por_rol": (df_partida_jugadores[["jugador_tipo_rol", "jugador_elo"]]),
        "elo_vs_ranking": (df_partida_jugadores[["jugador_elo", "jugador_posicion_ranking"]].dropna()),
        "partidas_por_dia": (df_partidas.dropna(subset=["fecha_partida"]).assign(fecha_dia=lambda df: df["fecha_partida"].dt.floor("D")).groupby("fecha_dia").size()),
        "bastiones_nether": (df_partidas["tipo_bastion_nether"].dropna().value_counts())
    }
    print(f"Categorias de estructuras Overworld: {len(datos['estructura_overworld']):,}")
    print(f"Registros validos para tiempo de resultado: {len(datos['tiempo_resultado']):,}")
    print(f"Registros validos para ELO por rol: {len(datos['elo_por_rol']):,}")
    print(f"Registros validos para ELO vs ranking: {len(datos['elo_vs_ranking']):,}")
    print(f"Dias disponibles para serie temporal: {len(datos['partidas_por_dia']):,}")
    print(f"Tipos de bastion registrados: {len(datos['bastiones_nether']):,}")
    return datos

"""
████████████████████████████████████████████████████████████████████████████
█  GRAFICAS                                                                █
████████████████████████████████████████████████████████████████████████████
"""
def generar_grafica_pastel(datos, ruta):
    valores = datos["estructura_overworld"]
    etiquetas = [ETIQUETAS_ESTRUCTURAS.get(valor, valor) for valor in valores.index]
    fig, ax = plt.subplots(figsize=(10, 7))
    separacion = [0.05] * len(valores)
    ax.pie(valores.values, labels=etiquetas, autopct="%1.1f%%", startangle=90, explode=separacion, wedgeprops={"edgecolor": "black", "linewidth": 1},  textprops={"fontsize": 10})
    ax.set_title("Distribucion de estructuras del Overworld", fontsize=14)
    plt.tight_layout()
    plt.savefig(ruta, dpi=220, bbox_inches="tight")
    plt.close()
    print(f"Pastel generado: {ruta}")

def generar_grafica_histograma(datos, ruta):
    valores = datos["tiempo_resultado"] / 60
    fig, ax = plt.subplots(figsize=(10, 7))
    max_minutos = math.ceil(valores.max())
    bins_personalizados = range(0, max_minutos + 5, 5)
    ax.hist(valores, bins=bins_personalizados, edgecolor="black")
    media = valores.mean()
    ax.axvline(media, color="crimson", linestyle="--", linewidth=2, label=f"Media: {media:.1f} min")
    ax.set_title("Distribucion del tiempo de resultado de las partidas", fontsize=14)
    ax.set_xlabel("Tiempo de resultado (minutos)")
    ax.set_ylabel("Cantidad de partidas")
    ax.xaxis.set_major_locator(MultipleLocator(10))
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    plt.tight_layout()
    plt.savefig(ruta, dpi=220, bbox_inches="tight")
    plt.close()
    print(f"Histograma generado: {ruta}")

def generar_grafica_caja(datos, ruta):
    df = datos["elo_por_rol"]
    grupos = []
    etiquetas = []
    for rol in sorted(df["jugador_tipo_rol"].unique()):
        valores = df.loc[df["jugador_tipo_rol"] == rol, "jugador_elo"].dropna()
        grupos.append(valores)
        etiquetas.append(f"Rol {rol}")
    registros_totales = len(datos["elo_por_rol"])
    registros_validos = sum(len(grupo) for grupo in grupos)
    registros_excluidos = registros_totales - registros_validos
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.boxplot(grupos, tick_labels=etiquetas)
    ax.set_title("Distribucion del ELO por tipo de rol", fontsize=14)
    ax.set_xlabel("Tipo de rol")
    ax.set_ylabel("ELO")
    ax.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    fig.subplots_adjust(bottom=0.20)
    fig.text(0.5, 0.045, f"Nota: {registros_excluidos:,} registros sin ELO fueron excluidos solamente de esta grafica por no disponer de una valoracion de ELO.", ha="center", va="center", fontsize=8.5)
    fig.text(0.5, 0.015, "La documentacion de MCSR Ranked indica que el ELO puede ser nulo cuando no se han terminado las partidas de posicionamiento.",ha="center", va="center", fontsize=8)
    plt.savefig(ruta, dpi=220, bbox_inches="tight")
    plt.close()
    print(f"Diagrama de caja generado: {ruta}")
    print(f"Registros sin ELO excluidos de la grafica: {registros_excluidos:,}")

def generar_grafica_dispersion(datos, ruta):
    df = datos["elo_vs_ranking"]
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.scatter(df["jugador_elo"], df["jugador_posicion_ranking"], alpha=0.35, s=12)
    ax.set_title("Relacion entre ELO y posicion en el ranking", fontsize=14)
    ax.set_xlabel("ELO")
    ax.set_ylabel("Posicion en ranking")
    ax.invert_yaxis()
    ax.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(ruta, dpi=220, bbox_inches="tight")
    plt.close()
    print(f"Diagrama de dispersion generado: {ruta}")

def generar_grafica_lineas(datos, ruta):
    serie = datos["partidas_por_dia"]
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.plot(serie.index, serie.values, marker="o", linewidth=2)
    for fecha, cantidad in serie.items():
        ax.annotate(f"{cantidad:,}", xy=(fecha, cantidad),xytext=(0, 8), textcoords="offset points", ha="center", va="bottom", fontsize=9)
    ax.set_title("Cantidad de partidas por dia", fontsize=14)
    ax.set_xlabel("Fecha")
    ax.set_ylabel("Cantidad de partidas")
    intervalor = max(1, len(serie) // 10) #Añadidura solo para reutilizacion
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=intervalor))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
    ax.grid(alpha=0.25)
    fig.autofmt_xdate()
    plt.tight_layout()
    plt.savefig(ruta, dpi=220, bbox_inches="tight")
    plt.close()
    print(f"Grafica de lineas generada: {ruta}")

def generar_grafica_barras(datos, ruta):
    valores = datos["bastiones_nether"]
    etiquetas = [ETIQUETAS_BASTIONES.get(valor, valor) for valor in valores.index]
    fig, ax = plt.subplots(figsize=(10, 7))
    barras = ax.bar(etiquetas, valores.values)
    ax.set_title("Distribucion de tipos de bastion del Nether", fontsize=14)
    ax.set_xlabel("Tipo de bastion")
    ax.set_ylabel("Cantidad de partidas")
    ax.grid(axis="y", alpha=0.25)
    ax.bar_label(barras, fmt="{:,.0f}", padding=4, fontsize=9)
    plt.tight_layout()
    plt.savefig(ruta, dpi=220, bbox_inches="tight")
    plt.close()
    print(f"Diagrama de barras generado: {ruta}")

"""
████████████████████████████████████████████████████████████████████████████
█  CONFIGURACIONES DE LAS GRAFICAS                                         █
████████████████████████████████████████████████████████████████████████████
"""
CONFIGURACION_GRAFICAS = [
    {"nombre": "Distribucion de estructuras Overworld", "tipo": "pastel", "funcion": generar_grafica_pastel, "ruta": SALIDA_GRAFICA_01},
    {"nombre": "Distribucion de tiempo de resultado", "tipo": "histograma", "funcion": generar_grafica_histograma, "ruta": SALIDA_GRAFICA_02},
    {"nombre": "Distribucion de ELO por rol", "tipo": "caja", "funcion": generar_grafica_caja, "ruta": SALIDA_GRAFICA_03},
    {"nombre": "Relacion entre ELO y ranking", "tipo": "dispersion", "funcion": generar_grafica_dispersion, "ruta": SALIDA_GRAFICA_04},
    {"nombre": "Cantidad de partidas por dia", "tipo": "lineas", "funcion": generar_grafica_lineas, "ruta": SALIDA_GRAFICA_05},
    {"nombre": "Distribucion de bastiones Nether", "tipo": "barras", "funcion": generar_grafica_barras, "ruta": SALIDA_GRAFICA_06}
]

"""
████████████████████████████████████████████████████████████████████████████
█  GENERACION DE LAS GRAFICAS                                              █
████████████████████████████████████████████████████████████████████████████
"""
def generar_graficas(datos):
    imprimir_titulo("GENERANDO VISUALIZACIONES")
    graficas_generadas = 0
    for configuracion in CONFIGURACION_GRAFICAS:
        nombre = configuracion["nombre"]
        tipo = configuracion["tipo"]
        funcion = configuracion["funcion"]
        ruta = configuracion["ruta"]
        print(f"\nGenerando: {nombre}")
        print(f"Tipo: {tipo}")
        funcion(datos, ruta)
        graficas_generadas += 1

    print(f"\nGraficas generadas exitosamente: {graficas_generadas}")
    return graficas_generadas

"""
████████████████████████████████████████████████████████████████████████████
█  GENERACION DEL RESUMEN                                                  █
████████████████████████████████████████████████████████████████████████████
"""
def mostrar_resumen(tablas, graficas_generadas):
    imprimir_titulo("RESUMEN DE LA PRACTICA 3")
    print(f"Partidas analizadas: {len(tablas['partidas']):,}")
    print(f"Participaciones jugador-partida: {len(tablas['partida_jugadores']):,}")
    print(f"Graficas generadas: {graficas_generadas}")
    print(f"Directorio de resultados: {RESULTADOS_DIR}")
    print("\nArchivos generados:")
    for configuracion in CONFIGURACION_GRAFICAS:
        print(f"  - {configuracion['ruta']}")

"""
████████████████████████████████████████████████████████████████████████████
█  CONFIGURACION DEL ESTILO DE LAS GRAFICAS                                █
████████████████████████████████████████████████████████████████████████████
"""
def configurar_estilo_graficas():
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams.update({"figure.dpi": 120, "savefig.dpi": 220, "axes.titlesize": 14, "axes.titleweight": "bold", "axes.labelsize": 11, "xtick.labelsize": 10, "ytick.labelsize": 10, "legend.fontsize": 9})

"""
████████████████████████████████████████████████████████████████████████████
█  EJECUCION PRACTICA 3                                                    █
████████████████████████████████████████████████████████████████████████████
"""
def ejecutar_act3():
    configurar_estilo_graficas()
    with registrar_salida(SALIDA_REPORTE):
        imprimir_titulo("ACT 3 - VISUALIZACION DE DATOS")
        tablas = cargar_tablas()
        datos = preparar_datos_graficas(tablas)
        graficas_generadas = generar_graficas(datos)
        mostrar_resumen(tablas, graficas_generadas)
        imprimir_titulo("ACT 3 COMPLETADA")

if __name__ == "__main__":
    ejecutar_act3()