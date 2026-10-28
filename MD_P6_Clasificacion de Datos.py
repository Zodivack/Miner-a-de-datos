"""
████████████████████████████████████████████████████████████████████████████
█  ACT 6 - CLASIFICACION DE DATOS CON K VECINOS MAS CERCANOS (KNN)         █
████████████████████████████████████████████████████████████████████████████

------------------------------------------------>
DESCRIPCION GENERAL DEL PROGRAMA
------------------------------------------------>
    Para esta practica se construyen y evaluan modelos de clasificacion para
    partidas de MCSR Ranked Temporada 10. Se tiene como objetivo en esta 
    practica el predecir si el primer jugador registrado en una partida
    sera el ganador o si el segunda jugador lo sera. Para esto se usaron las 
    tablas de partidas.csv, partidas_jugadores.csv y cambios_elo.csv mediante 
    el identificador de la artida y el UUID de cada jugador. 

    La variable objetivo se reconstruye comparando el uuid_ganador con los
    UUID de ambos participantes. El valor 1 representa la victoria del
    jugador 1 y el 0 representa un victoria del jugador 2. Cuando
    existe una etiqueta original valida, se compara con la etiqueta
    reconstruida para detectar posibles diferencias.

    Una vez validadas las claves, correspondencia de los jugadores, etiquetas
    y los valores necesarios para calcular el ELO, se seleccionan las 
    partidas que pueden utilizarse en la clasificacion.

    De forma extra, se compara dos implemenatciones del algoritmo K vecinos
    mas cercanos; una mediante scikit-learn y otra propia. Ambas se evaluan
    bajo el mismo conjunto de entrenamiento, datos de prueba, mismo
    procesamiento y las misma configuracion de k.

------------------------------------------------>
MODELO DE CLASIFICACION KNN
------------------------------------------------>
    Variable Objetivo (Y): 
        -> victoria_jugador_1

    Variables predictorias (X):
        -> elo_previo_jugador_1_estimado
        -> elo_previo_jugador_2_estimado
        -> estructura_overworld
        -> tipo_bastion_nether

    Ya se ha mencionado en anteriores practicas, pero el ELO previo estimado
    de cada jugador se reconstruye; elo_previo_estimado = elo - cambio_elo.
    La reconstruccion se considera como una estimacion del ELO anterior al
    cambio registrado. Esto dado a la que la documentacion de la API no 
    especifica explicitamente este campo.

    Los dos ELO se tratan como variables numericas y se estandarizan mediante
    StandardScaler. La caracteristicas estructura_overworld y tipo_bastion_nether
    se tratan como variables categoricas; los valores ausentes se sustituyen por 
    SIN_DATOS y las categorias se tranforma en indicadores mediante OneHotEncoder.


------------------------------------------------>
COMPONENTES DENTRO DEL ANALISIS
------------------------------------------------>
    -> Calidad de datos:
        Se verifican las columnas requeridas, claves, existencia de los registros
        relacionados y la presencia de exactamente dos jugadores con indices
        validos por partida. Del mismo modo, se revisan los ganadores ausentes,
        los calores de ELO faltantes o no validos y las posibles discrepancias 
        entre la etiqueta original y la reconstruida desde uuid_ganador

    -> Preparacion del dataset:
        Se integran las tablas correspondientes mediante las claves correspondientes
        y se calcula una estimacion del ELO previo para cada jugador

        Las partidas sin ganador identificables y aquellas en las que no dispone de 
        ambos ELO previos estimados validos se excluyerion, por lo que al no cumplir
        cons los requisitos no participan en el entrenamiento ni en la evaluacion.
        Sin embargo, se conservaron aquellas partidas sin completar pero que 
        cumplen los requisitos del modelo, del mismo modo, aquellas partidas con 
        tiempo iguales a cero tambien se concervan, ya que el tiempo ni es una
        viariable predictora

    -> Division de entrenamiento y prueba:
        Los datos se dividen en un 70% para entrenamiento y un 30% para pruebas. Asi
        mismo, se utiliza un semilla aleatoria fija y una division estratificada para
        conservar aproximadamente la proporcion de ambas clases

    -> Preprocesamiento:
        Las variables numericas se estandarizan y las categoricas se imputan y 
        codifican.  El preprocesamiento se incorpora al procedimiento de ajuste para
        evitar que los parametros aprendidos durante cada particion de validacion 
        crucen hacia su conjunto de evaluacion

    -> Seleccion de hiperparametros:
        Se utilizan validacion cruzada con tres particiones sobre el conjunto de
        entrenamiento. Se prueban valores de K = 3, 5, 7, 9, 11, 15, 21, 24,
        27 y 30, junto con las ponderaciones uniform y distance. La seleccion se 
        realiza con base F1 macro medio de la validacion cruzada

    -> Evaluacion del modelo:
        Una vez seleccionada la configuracion, se evalua el modelo en el conjunto de
        prueba reservado. Se calculan exactitud, exactitud balanceada, precision,
        recall, F1 de la clase 1, F1 macro y AUC ROC. Tambien, se generan matrices 
        de confusion y un reporte por clase

    -> Comparacion con un modelo de referencia: 
        Se utiliza DummyClassifier con la estrategia most_frequent, que siempre predice
        la clase mas frecuente en el entrenamiento. Esto permite comprobar si KNN 
        aporta capacidad predictiva por encima de una estrategia que no considera
        las caracteristicas de las partidas

    -> Comparacion de implementaciones: 
        La propia implementacion calcula las distancias entre las obsevaciones, 
        selecciona los K vecinos mas cercanos y determina la clase mediante 
        votacion. Sus predicciones se compara con las de Scikit-learn utilizando
        los mismos datos transformados, la misma division de entrenamiento, prueba
        y los mismo hiperparametros seleccionados

------------------------------------------------>
JUSTIFICACION DE DECISIONES TOMADAS
------------------------------------------------>
    ->  Se utiliza una division de 70/30 porque se conserva una cantidad amplia de
        observaciones para entrenar y reservar suficientes partidas para evaluar el
        rendimiento fuera del entrenamiento
    
    ->  Por estratificacion mantiene aproximadamente la proporcion de victorias de ambos
        jugadores en entrenamiento y prueba, facilitando una comparacion mas representativa
        entre las clases

    ->  Las variables categoricas se codifican mediante OneHotEncoder. De esa forma, las
        categorias no se interpretan como cantidades numericas ordenadas artificialmente

    ->  Se estandarizo los ELO porque KNN utiliza distancias, y esto evita que la escala
        numerica de estas variables domine injustamente el calculo de proximidad.

    ->  Se utiliza F1 macro para seleccionar la configuracion porque calcula el F1 de 
        ambas clases y les asigna la misma importancia, independientemente de sus frecuencias

    ->  Se generan matrices de confusion para observar las victorias correctamente
        clasificadas y los errores de cada clase. Las otras metricas complementarias permiten
        analizar aspectos que la exactitud por si sola no representa completamente.

------------------------------------------------>
INTERPRETACION DE RESULTADOS
------------------------------------------------>
    Al final del datase completo se utilizaron 42,472 partidas: 21,274 correspondientes a
    victorias del jugador 2 (clase 0), equivalente a un 50.089%, y el resto(21,198) a 
    victorias del jugador 1 (clase 1), equivalente a un 49.911%. Por lo que, la
    distribucion de clases resulto practicamente equilibrada, asegurando que no hay un 
    predominio de una de las victorias.

    En cuanto a las divisiones de las partidas se mandaron 29,730 partidas a entrenamiento y
    12,742 para pruebas. Mediante validacion curzada se seleciono que la mejor opcion era una
    K de 21 con una ponderacion uniforme, ya que alcanzo un F1 macro medio de 0.77095.

    La implementacion de Scikit-learn obtuvo una exactitud de de 0.77366, una exactitud balanceada 
    de 0.77365, un F1 macro de 0.77365 y un AUC ROC de 0.856. La precision de la clase 1 fue de 
    0.77605, su recall fue de 0.76824 y su F1 fue de 0.77212. Estos resultados muestran que el modelo
    identifica correctamente una proporcion importante de las victorias, sin embargo, matiene errores
    de clasificacion algo altos en ambas clases.

    El clasificador de referencia obtuvo una exactitud de 0.50086, una exactitud balanceada de 0.5 y 
    un F1 macro de 0.33372. Esta diferencia de rendimiento da a entender que KNN aprovecha bien la
    informacion presente a los predictores y supera ampliamente la estrategia de solo elegir la clase
    mayoritaria.

    Por otra parte, la implementacion propia alcanzo las mismas metricas que Scikit-learn en las 
    12,742 partidas de prueba, con una coincidencia del 100%. Aunque el AUC ROC fue 0.85599 para la 
    implementacion propia y 0.856 para Scikit-learn; pero esta diferencia es muy pequennia. Esta
    coincidencia se explica porque ambas implementaciones usan el mismo conjunto de datos transformados,
    la misma distancia euclidiana, los mismos 24 vecinos y una ponderacion por distancia.

    Lo que se puede decir es que actualmente el modelo presenta un rendimiento predictivo bueno, superior
    al clasificador de referencia. Pero, los resultados deben interpretarse considerando la estimacion
    de ELO previo y el hecho de que los jugadores pueden aparecer tanto en entrenamiento como en prueba

------------------------------------------------>
ARCHIVOS DE SALIDA
------------------------------------------------>
    El programa genera los siguientes resultados en Act_6/resultados/:

        -> datos_modelo_knn.csv
            Dataset final utilizado en la clasificacion.

        -> distribucion_clases.csv
            Frecuencias y porcentajes de ambas clases.

        -> resultados_validacion_cruzada.csv
            Rendimiento de las configuraciones probadas.

        -> metricas_comparacion_knn.csv
            Comparacion de KNN de Scikit-learn, KNN propio y el clasificador    
            de referencia.

        -> matrices_confusion.csv
            Conteos de clasificaciones correctas e incorrectas.

        -> reporte_por_clase.csv
            Metricas individuales para cada clase.

        -> predicciones_prueba_knn.csv
            Etiquetas reales y predicciones del conjunto de prueba.

        -> distribucion_clases.png
            Grafica de la distribucion de la variable objetivo.

        -> seleccion_k_validacion.png
            Grafica del rendimiento de las configuraciones de KNN.

        -> comparacion_matrices_confusion.png
            Comparacion visual de los resultados de clasificacion.

        -> reporte_act_6_knn.txt
            Reporte con los parametros, metricas y consideraciones de 
            la ejecucion.
"""

from pathlib import Path
from contextlib import contextmanager
import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, classification_report, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

"""
████████████████████████████████████████████████████████████████████████████
█  CONSTANTES Y RUTAS DE ARCHIVOS                                          █
████████████████████████████████████████████████████████████████████████████
"""
SEMILLA_ALEATORIA = 42
PROPORCION_PRUEBA = 0.30
NUMERO_PARTICIONES_CV = 3
N_JOBS_CV = max(1, min(4, os.cpu_count() or 1))
MINIMO_FILAS_MODELO = 30
VALORES_K = [3, 5, 7, 9, 11, 15, 21, 24, 27, 30]
PONDERACIONES = ["uniform", "distance"]
CLAVE_PARTIDA = ["id_partida"]
CLAVE_JUGADOR = ["id_partida", "jugador_uuid"]
VARIABLE_OBJETIVO = "victoria_jugador_1"
VARIABLES_NUMERICAS = ["elo_previo_jugador_1_estimado", "elo_previo_jugador_2_estimado"]
VARIABLES_CATEGORICAS = ["estructura_overworld", "tipo_bastion_nether"]
VARIABLES_PREDICTORAS = VARIABLES_NUMERICAS + VARIABLES_CATEGORICAS

def resolver_base_dir():
    candidatos = [Path.cwd() / "MCSR_Ranked", Path.cwd(), Path(__file__).resolve().parent / "MCSR_Ranked", Path(__file__).resolve().parent]
    archivos_requeridos = [Path("data/final/main/partidas.csv"), Path("data/final/main/partida_jugadores.csv"), Path("data/final/aux/cambios_elo.csv")]
    for candidato in candidatos:
        if all((candidato / archivo).is_file() for archivo in archivos_requeridos):
            return candidato.resolve()
    raise FileNotFoundError("No se localizo la carpeta del proyeco con los CSV requeridos. Ejecute el programa desde la raiz del repo o coloca el script junto a la carpeta MCSR_Ranked") 

BASE_DIR = resolver_base_dir()
MAIN_DIR = BASE_DIR / "data" / "final" / "main"
AUX_DIR = BASE_DIR / "data" / "final" / "aux"
ACT6_DIR = BASE_DIR / "Act_6"
RESULTADOS_DIR = ACT6_DIR / "resultados"
RESULTADOS_DIR.mkdir(parents=True, exist_ok=True)
CSV_PARTIDAS = MAIN_DIR / "partidas.csv"
CSV_PARTIDA_JUGADORES = MAIN_DIR / "partida_jugadores.csv"
CSV_CAMBIOS_ELO = AUX_DIR / "cambios_elo.csv"
REPORTE_TXT = RESULTADOS_DIR / "reporte_act_6_knn.txt"

"""
████████████████████████████████████████████████████████████████████████████
█  FUNCIONES GENERALES Y REGISTRO DE SALIDA EN CONSOLA Y ARCHIVO TXT       █
████████████████████████████████████████████████████████████████████████████
"""
def imprimir_titulo(texto):
    print(f"\n{'█' * 100}\n█{f" {texto} ".center(98, " ")}█\n{'█' * 100}")

def imprimir_tabla(tabla):
    if not isinstance(tabla, pd.DataFrame):
        raise TypeError("???????????????")
    if tabla.empty:
        print("(Sin registros para mostrar)")
        return
    columnas = [" ".join(str(columna).split()) for columna in tabla.columns]

    def es_numerica(serie):
        if pd.api.types.is_numeric_dtype(serie.dtype):
            return True
        valores = serie.dropna()
        if valores.empty:
            return False
        texto = valores.astype(str).str.strip().str.replace(",", "", regex=False).str.rstrip("%")        
        try:
            pd.to_numeric(texto, errors="raise")
            return True
        except (ValueError, TypeError):
            return False
        
    columnas_numericas = [es_numerica(tabla.iloc[:, indice]) for indice in range(tabla.shape[1])]
    tabla_texto = tabla.astype(object).where(tabla.notna(), "NaN").astype(str)
    filas = [[" ".join(valor.split()) for valor in fila] for fila in tabla_texto.itertuples(index=False, name=None)]
    anchos = [len(columna) for columna in columnas]
    for fila in filas:
        for indice, valor in enumerate(fila):
            if len(valor) > anchos[indice]:
                anchos[indice] = len(valor)
    separador = "+-" + "-+-".join("-" * ancho for ancho in anchos) + "-+"

    def formatear_fila(fila, encabezado=False):
        celdas = []
        for indice, valor in enumerate(fila):
            celdas.append(valor.rjust(anchos[indice]) if not encabezado and columnas_numericas[indice] else valor.ljust(anchos[indice]))
        return "| " + " | ".join(celdas) + " |"

    print(separador)
    print(formatear_fila(columnas, encabezado=True))
    print(separador)
    for fila in filas:
        print(formatear_fila(fila))
    print(separador)

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
█  FUNCIONES GENERALES Y REGISTRO DE SALIDA EN CONSOLA Y ARCHIVO TXT       █
████████████████████████████████████████████████████████████████████████████
"""
def normalizar_id(serie): return pd.to_numeric(serie, errors="coerce").astype("Int64")

def normalizar_texto(serie): return serie.astype("string").str.strip().replace(r"^\s*$", pd.NA, regex=True)

def es_verdadero(serie): return serie.astype("string").str.strip().str.lower().isin(["true", "1", "yes", "si", "sí"])

def cargar_dataset(ruta, nombre, columnas):
    if not ruta.is_file(): 
        raise FileNotFoundError(f"No se encontro el archivo requerido: {ruta}")
    columnas_disponibles = pd.read_csv(ruta, nrows=0).columns.tolist()
    columnas_faltantes = [columna for columna in columnas if columna not in columnas_disponibles]
    if columnas_faltantes:
        raise ValueError(f"Faltan columnas requeridas en {ruta}: {columnas_faltantes}")
    df = pd.read_csv(ruta, usecols=columnas)
    print(f"Archivo: {ruta}\n{nombre:25} {len(df):>10,} filas | {len(df.columns):>2} columnas")
    return df

def validar_claves_unicas(tabla, nombre, claves):
    columnas_inexistentes = [col for col in claves if col not in tabla.columns]
    if columnas_inexistentes:
        raise ValueError(f"La tabla {nombre} no contiene las columnas clave requeridas: {columnas_inexistentes}")
    mascara_incompletas = tabla[claves].isna().any(axis=1)
    filas_incompletas = int(mascara_incompletas.sum())
    mascara_completas = ~mascara_incompletas
    mascara_duplicadas = pd.Series(False, index=tabla.index)
    if mascara_completas.any():
        mascara_duplicadas.loc[mascara_completas] = tabla.loc[mascara_completas].duplicated(claves, keep=False).to_numpy()
    filas_duplicadas = int(mascara_duplicadas.sum())
    print(f"{nombre:24} filas con clave incompleta: {filas_incompletas:>8,}")
    print(f"{'':24} filas con clave duplicada: {filas_duplicadas:>8,}")
    if filas_incompletas or filas_duplicadas:
        mascara_problemas = mascara_incompletas | mascara_duplicadas
        muestras = tabla.loc[mascara_problemas, claves].head(10)
        raise ValueError(f"La tabla {nombre} no tiene una clave unica y completa ({claves}).\nIncompletos = {filas_incompletas}; duplicados reales = {filas_duplicadas}.\nA revision:\n{muestras.to_string(index=False)}")

"""
████████████████████████████████████████████████████████████████████████████
█  CARGAR DATASET Y VALIDACION DE ESTRUCTURA                               █
████████████████████████████████████████████████████████████████████████████
"""
def cargar_tablas():
    imprimir_titulo("CARGANDO Y VALIDANDO TABLAS")
    config_datasets = {
        "partidas": {
            "ruta": CSV_PARTIDAS,
            "columnas": ["id_partida", "uuid_ganador", "estructura_overworld", "tipo_bastion_nether", "tiempo_resultado_ms", "partida_sin_completarse", "victoria_jugador_1"],
            "claves": CLAVE_PARTIDA,
            "transformar": lambda df: df.assign(id_partida=normalizar_id(df["id_partida"]), uuid_ganador=normalizar_texto(df["uuid_ganador"]).str.lower(), victoria_jugador_1_fuente=pd.to_numeric(df.pop("victoria_jugador_1"), errors="coerce"), tiempo_resultado_ms=pd.to_numeric(df["tiempo_resultado_ms"], errors="coerce"), estructura_overworld=normalizar_texto(df["estructura_overworld"]), tipo_bastion_nether=normalizar_texto(df["tipo_bastion_nether"]))
        },
        "partida_jugadores": {
            "ruta": CSV_PARTIDA_JUGADORES,
            "columnas": ["id_partida", "indice_jugador", "jugador_uuid"],
            "claves": CLAVE_JUGADOR,
            "transformar": lambda df: df.assign(id_partida=normalizar_id(df["id_partida"]), jugador_uuid=normalizar_texto(df["jugador_uuid"]).str.lower(), indice_jugador=pd.to_numeric(df["indice_jugador"], errors="coerce"))
        },
        "cambios_elo": {
            "ruta": CSV_CAMBIOS_ELO,
            "columnas": ["id_partida", "jugador_uuid", "cambio_elo", "elo"],
            "claves": CLAVE_JUGADOR,
            "transformar": lambda df: df.assign(id_partida=normalizar_id(df["id_partida"]), jugador_uuid=normalizar_texto(df["jugador_uuid"]).str.lower(), elo=pd.to_numeric(df["elo"], errors="coerce"), cambio_elo=pd.to_numeric(df["cambio_elo"], errors="coerce"))
        }
    }
    tablas = {}
    for nombre, cfg in config_datasets.items():
        tabla = cargar_dataset(cfg["ruta"], nombre, cfg["columnas"])
        tabla = cfg["transformar"](tabla)
        validar_claves_unicas(tabla, nombre, cfg["claves"])
        tablas[nombre] = tabla
    return tablas["partidas"], tablas["partida_jugadores"], tablas["cambios_elo"]

def mostrar_calidad(partidas, jugadores, cambios):
    imprimir_titulo("RESUMEN DE CALIDAD DE LOS DATOS DE ENTRADA")
    tiempo_ms = partidas["tiempo_resultado_ms"].to_numpy(dtype=float, na_value=np.nan)
    tiempo_finito = np.isfinite(tiempo_ms)
    especificaciones = [
        ("Partidas originales", len(partidas)), 
        ("Partidas con id de partida faltante", partidas["id_partida"].isna().sum()), 
        ("Etiquetas originales ausentes o no binarias", (~partidas["victoria_jugador_1_fuente"].isin([0, 1])).sum()),
        ("Filas en partidas_jugadores", len(jugadores)),
        ("Participaciones con clave incompleta", jugadores[CLAVE_JUGADOR].isna().any(axis=1).sum()),
        ("Cambios ELO con clave incompleta", cambios[CLAVE_JUGADOR].isna().any(axis=1).sum()),
        ("Cambios con elo faltante", cambios["elo"].isna().sum()),
        ("Cambios con cambio_elo faltante", cambios["cambio_elo"].isna().sum()),
        ("Partidas con ganador ausente", partidas["uuid_ganador"].isna().sum()),
        ("Tiempos faltantes o no finitos (ms)", (~tiempo_finito).sum()),
        ("Partidas con tiempo cero (ms)", (tiempo_finito & (tiempo_ms == 0)).sum()),
        ("Partidas con tiempo negativo (ms)", (tiempo_finito & (tiempo_ms < 0)).sum()),
        ("Partidas marcadas como sin completar", es_verdadero(partidas["partida_sin_completarse"]).sum())
    ]
    indicadores = [{"Indicador": descripcion, "Cantidad": int(valor)} for descripcion, valor in especificaciones]
    imprimir_tabla(pd.DataFrame(indicadores))

def construir_dataset_modelo(partidas, jugadores, cambios):
    total_partidas = len(partidas)
    id_partidas_existentes = set(partidas["id_partida"].dropna())
    jugadores_validos_clave = jugadores[jugadores["id_partida"].notna() & jugadores["jugador_uuid"].notna() & jugadores["indice_jugador"].notna()]
    jugadores_fuera = int((~jugadores_validos_clave["id_partida"].isin(id_partidas_existentes)).sum())
    jugadores_validos_clave = jugadores_validos_clave[jugadores_validos_clave["id_partida"].isin(id_partidas_existentes)]
    cardinalidad = jugadores_validos_clave.groupby("id_partida").agg(numero_filas=("jugador_uuid", "size"), jugadores_unicos=("jugador_uuid", "nunique"), indices_unicos=("indice_jugador", "nunique"), indice_minimo=("indice_jugador", "min"), indice_maximo=("indice_jugador", "max"))
    ids_dos_jugadores = set(cardinalidad.index[(cardinalidad["numero_filas"] == 2) & (cardinalidad["jugadores_unicos"] == 2) & (cardinalidad["indices_unicos"] == 2) & (cardinalidad["indice_minimo"] == 0)& (cardinalidad["indice_maximo"] == 1)])
    ids_sin_dos = id_partidas_existentes - ids_dos_jugadores
    jugadores_dos = jugadores_validos_clave[jugadores_validos_clave["id_partida"].isin(ids_dos_jugadores)].sort_values(["id_partida", "indice_jugador"], kind="stable").assign(posicion_modelo=lambda df: df.groupby("id_partida").cumcount() + 1)
    cambios_clave = cambios.dropna(subset=["id_partida", "jugador_uuid"])
    participaciones = jugadores_dos.merge(cambios_clave[CLAVE_JUGADOR + ["elo", "cambio_elo"]], on=CLAVE_JUGADOR, how="left", validate="one_to_one", indicator=True).assign(elo_previo_estimado=lambda df: df["elo"] - df["cambio_elo"])
    valores_elo = participaciones[["elo", "cambio_elo", "elo_previo_estimado"]].to_numpy(dtype=float)
    participaciones["elo_previo_valido"] = np.isfinite(valores_elo).all(axis=1) & (participaciones["elo_previo_estimado"] > 0)
    uuids = participaciones.pivot(index="id_partida", columns="posicion_modelo", values="jugador_uuid").rename(columns={1: "jugador_1_uuid", 2: "jugador_2_uuid"})
    ratings = participaciones.pivot(index="id_partida", columns="posicion_modelo", values="elo_previo_estimado").rename(columns={1: "elo_previo_jugador_1_estimado", 2: "elo_previo_jugador_2_estimado"})
    ancho = uuids.join(ratings, how="left").reset_index()
    datos = partidas.merge(ancho, on="id_partida", how="inner", validate="one_to_one")
    ganador = normalizar_texto(datos["uuid_ganador"])
    uuid_1 = normalizar_texto(datos["jugador_1_uuid"])
    uuid_2 = normalizar_texto(datos["jugador_2_uuid"])
    gana_1 = ganador.notna() & (ganador == uuid_1)
    gana_2 = ganador.notna() & (ganador == uuid_2)
    ganador_valido = gana_1 | gana_2
    ganador_ausente = ganador.isna()
    ganador_ajeno = ganador.notna() & ~ganador_valido
    datos[VARIABLE_OBJETIVO] = pd.Series(pd.NA, index=datos.index, dtype="Int64")
    datos.loc[gana_1, VARIABLE_OBJETIVO] = 1
    datos.loc[gana_2, VARIABLE_OBJETIVO] = 0
    etiqueta_fuente = pd.to_numeric(datos["victoria_jugador_1_fuente"], errors="coerce")
    etiqueta_fuente_valida = etiqueta_fuente.isin([0, 1])
    etiquetas_comparables = ganador_valido & etiqueta_fuente_valida
    etiquetas_discrepantes = etiquetas_comparables& (etiqueta_fuente != datos[VARIABLE_OBJETIVO].astype("Float64")).fillna(False)
    if etiquetas_discrepantes.any():
        discordancias = datos.loc[etiquetas_discrepantes, ["id_partida", "jugador_1_uuid", "jugador_2_uuid", "uuid_ganador", "victoria_jugador_1_fuente", VARIABLE_OBJETIVO]].copy()
        discordancias.to_csv(RESULTADOS_DIR / "discordancias_etiquetas.csv", index=False, encoding="utf-8-sig")
        print(f"\nADVERTENCIA: se guardaron las etiquetas discordantes en {RESULTADOS_DIR / 'discordancias_etiquetas.csv'}")
    elo_1 = pd.to_numeric(datos["elo_previo_jugador_1_estimado"], errors="coerce").to_numpy(dtype=float, na_value=np.nan)
    elo_2 = pd.to_numeric(datos["elo_previo_jugador_2_estimado"], errors="coerce").to_numpy(dtype=float, na_value=np.nan)
    elo_bilateral_valido = np.isfinite(elo_1) & np.isfinite(elo_2) & (elo_1 > 0) & (elo_2 > 0)
    mascara_final = ganador_valido.to_numpy() & elo_bilateral_valido
    datos_modelo = datos.loc[mascara_final].copy().reset_index(drop=True)
    datos_modelo[VARIABLE_OBJETIVO] = datos_modelo[VARIABLE_OBJETIVO].astype(int)
    for columna in VARIABLES_CATEGORICAS:
        serie = normalizar_texto(datos_modelo[columna])
        datos_modelo[columna] = serie.astype(object).where(serie.notna(), np.nan)
    emparejamiento = participaciones["_merge"].eq("both")
    tiempo_ms = datos_modelo["tiempo_resultado_ms"].to_numpy(dtype=float, na_value=np.nan)
    tiempo_finito = np.isfinite(tiempo_ms)
    resumen = {
            "partidas_originales": total_partidas,
            "participaciones_con_clave_incompleta_excluidas": int(jugadores[CLAVE_JUGADOR + ["indice_jugador"]].isna().any(axis=1).sum()),
            "participaciones_fuera_de_partidas_existentes": jugadores_fuera,
            "partidas_sin_exactamente_dos_jugadores_con_indices_validos": len(ids_sin_dos),
            "partidas_con_dos_jugadores_evaluadas": len(datos),
            "participaciones_sin_coincidencia_en_cambios_elo": int((~emparejamiento).sum()),
            "participaciones_con_elo_previo_no_valido": int((~participaciones["elo_previo_valido"]).sum()),
            "partidas_con_ganador_ausente": int(ganador_ausente.sum()),
            "partidas_con_ganador_ajeno_a_los_dos_jugadores": int(ganador_ajeno.sum()),
            "partidas_con_ganador_valido": int(ganador_valido.sum()),
            "partidas_con_ambos_elo_previos_validos": int(elo_bilateral_valido.sum()),
            "partidas_finales_para_el_modelo": len(datos_modelo),
            "victorias_jugador_1": int((datos_modelo[VARIABLE_OBJETIVO] == 1).sum()),
            "victorias_jugador_2": int((datos_modelo[VARIABLE_OBJETIVO] == 0).sum()),
            "etiquetas_fuente_validas_comparadas": int(etiquetas_comparables.sum()),
            "discordancias_etiqueta_fuente_vs_uuid_ganador": int(etiquetas_discrepantes.sum()),
            "etiquetas_fuente_ausentes_o_no_binarias": int((~etiqueta_fuente_valida).sum()),
            "partidas_finales_con_tiempo_cero_conservadas": int((tiempo_finito & (tiempo_ms == 0)).sum()),
            "partidas_finales_con_tiempo_faltante_o_no_finito": int((~tiempo_finito).sum()),
            "partidas_finales_con_tiempo_negativo": int((tiempo_finito & (tiempo_ms < 0)).sum()),
            "partidas_sin_completar_con_ganador_valido_antes_de_validar_elo": int((es_verdadero(datos["partida_sin_completarse"]) & ganador_valido).sum()),
            "partidas_sin_completar_finales_en_modelo": int(es_verdadero(datos_modelo["partida_sin_completarse"]).sum())
        }
    if resumen["discordancias_etiqueta_fuente_vs_uuid_ganador"] > 0:
        print("\nADVERTENCIA: la columna victoria_jugador_1 no coincide con la etiqueta reconstruida desde uuid_ganador en algunos registros. Se recomienda revisar las discordancias antes de presentar los resultados.")
    imprimir_titulo("RESUMEN DE PREPARACION DEL DATASET")
    imprimir_tabla(pd.DataFrame([{"Indicador": nombre.replace("_", " ").capitalize(), "Cantidad": cantidad} for nombre, cantidad in resumen.items()]))
    print("\nNota IMPORTANTE sobre el ELO. Se utiliza una estimacion del elo previo a la partida; elo_previo_estimado = elo - cambio_elo. Es una mera reconstruccion basada en la interpretacion de los datos; la documentacion oficial no especifica de forma concluyente el elo previo")
    if datos_modelo.empty: raise ValueError("No hay partidas con etiqueta y ambos ELO previos estimados son validos.")
    if datos_modelo[VARIABLE_OBJETIVO].nunique() < 2: raise ValueError("El dataset final solo contiene informacion sobre una clase. Es necesario victorias de ambos jugadores.")
    columnas_salida = ["id_partida", "jugador_1_uuid", "jugador_2_uuid", "elo_previo_jugador_1_estimado", "elo_previo_jugador_2_estimado", "estructura_overworld", "tipo_bastion_nether", VARIABLE_OBJETIVO, "uuid_ganador", "victoria_jugador_1_fuente", "tiempo_resultado_ms", "partida_sin_completarse"]
    ruta_datos = RESULTADOS_DIR / "datos_modelo_knn.csv"
    datos_modelo[columnas_salida].to_csv(ruta_datos, index=False, encoding="utf-8-sig")
    print(f"\nDataset preparado guardado en: {ruta_datos}")
    frecuencias = datos_modelo[VARIABLE_OBJETIVO].value_counts().reindex([0, 1], fill_value=0)
    tabla_clases = pd.DataFrame([{"Clase": "0 - Gana jugador 2", "Cantidad": int(frecuencias.loc[0]), "Porcentaje": 100 * frecuencias.loc[0] / len(datos_modelo)}, {"Clase": "1 - Gana jugador 1", "Cantidad": int(frecuencias.loc[1]), "Porcentaje": 100 * frecuencias.loc[1] / len(datos_modelo)}])
    imprimir_titulo("DISTRIBUCION DE LA VARIABLE OBJETIVO")
    imprimir_tabla(tabla_clases.round(3))
    tabla_clases.to_csv(RESULTADOS_DIR / "distribucion_clases.csv", index=False, encoding="utf-8-sig")
    return datos_modelo


def crear_codificador():
    try: return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError: return OneHotEncoder(handle_unknown="ignore", sparse=False)

def crear_preprocesador():
    return ColumnTransformer(transformers=[("numericas", Pipeline(steps=[("escalar", StandardScaler())]), VARIABLES_NUMERICAS), ("categoricas",Pipeline(steps=[("imputar", SimpleImputer(strategy="constant", fill_value="SIN_DATO")), ("codificar", crear_codificador())]), VARIABLES_CATEGORICAS)], remainder="drop")

def crear_pipeline_knn(): 
    return Pipeline(steps=[("preparacion", crear_preprocesador()), ("knn", KNeighborsClassifier(algorithm="brute", n_jobs=1))])

def seleccionar_indices_vecinos(distancias_cuadradas, k):
    umbral = np.max(distancias_cuadradas[np.argpartition(distancias_cuadradas, kth=k - 1)[:k]])
    estrictamente_menores = np.flatnonzero(distancias_cuadradas < umbral)
    iguales = np.flatnonzero(distancias_cuadradas == umbral)
    faltan = k - len(estrictamente_menores)
    seleccionados = np.concatenate([estrictamente_menores, iguales[:faltan]])
    return seleccionados[np.lexsort((seleccionados, distancias_cuadradas[seleccionados]))]

def knn_propio(X_entrenamiento, Y_entrenamiento, X_nuevos, k, ponderacion="uniform", tamannio_lote=256):
    X_entrenamiento = np.asarray(X_entrenamiento, dtype=float)
    X_nuevos = np.asarray(X_nuevos, dtype=float)
    Y_entrenamiento = np.asarray(Y_entrenamiento, dtype=int)
    clases = np.unique(Y_entrenamiento)
    validaciones = [
        (lambda: X_entrenamiento.ndim == 2 and X_nuevos.ndim == 2, "Las matrices de entrada deben ser bidimensionales"),
        (lambda: X_entrenamiento.shape[0] > 0 and X_entrenamiento.shape[1] > 0, "La matriz de entrenamiento debe tener filas y caracteristicas"),
        (lambda: X_entrenamiento.shape[1] == X_nuevos.shape[1], "Entrenamiento y prediccion no tienen la misma cantidad de caracteristicas"),
        (lambda: len(X_entrenamiento) == len(Y_entrenamiento), "X_entrenamiento y Y_entrenamiento no tienen la misma cantidad de filas"),
        (lambda: isinstance(k, (int, np.integer)) and 1 <= k <= len(X_entrenamiento), "K debe ser un entero positivo y no superar el numero de filas de entrenamiento."),
        (lambda: isinstance(tamannio_lote, (int, np.integer)) and tamannio_lote >= 1, "El tamannio del lote debe ser un entero positivo."),
        (lambda: np.array_equal(clases, np.array([0, 1])), "Esta implementacion propia requiere etiquetas binarias codificadas como 0 y 1."),
        (lambda: ponderacion in ["uniform", "distance"], "La ponderacion debe ser 'uniform' o 'distance'."),
        (lambda: np.isfinite(X_entrenamiento).all() and np.isfinite(X_nuevos).all(), "Las matrices preprocesadas contienen valores no finitos.")
    ]
    for condicion, mensaje in validaciones:
        if not condicion():
            raise ValueError(mensaje)
    n_muestras = len(X_nuevos)
    norma_entrenamiento = np.sum(X_entrenamiento ** 2, axis=1)
    predicciones = np.empty(n_muestras, dtype=clases.dtype)
    probabilidades = np.zeros((n_muestras, 2), dtype=float)
    es_uniforme = ponderacion == "uniform"
    for inicio in range(0, n_muestras, tamannio_lote):
        fin = min(inicio + tamannio_lote, n_muestras)
        lote = X_nuevos[inicio:fin]
        norma_lote = np.sum(lote ** 2, axis=1)
        distancias_cuadradas = lote @ X_entrenamiento.T
        distancias_cuadradas *= -2
        distancias_cuadradas += norma_lote[:, None]
        distancias_cuadradas += norma_entrenamiento[None, :]
        np.maximum(distancias_cuadradas, 0, out=distancias_cuadradas)
        for posicion_local, distancias_2 in enumerate(distancias_cuadradas):
            vecinos = seleccionar_indices_vecinos(distancias_2, k)
            etiquetas_vecinos = Y_entrenamiento[vecinos]
            if es_uniforme:
                votos_1 = np.count_nonzero(etiquetas_vecinos)
                votos_0 = k - votos_1
            else:
                distancias = np.sqrt(distancias_2[vecinos])
                ceros = distancias == 0
                if ceros.any():
                    pesos = ceros.astype(float)
                else:
                    pesos = 1.0 / distancias
                votos_1 = pesos[etiquetas_vecinos == 1].sum()
                votos_0 = pesos[etiquetas_vecinos == 0].sum()
            total_votos = votos_0 + votos_1
            if total_votos <= 0:
                votos_0 = votos_1 = 1.0
                total_votos = 2.0
            idx_global = inicio + posicion_local
            probabilidades[idx_global, 0] = votos_0 / total_votos
            probabilidades[idx_global, 1] = votos_1 / total_votos
            predicciones[idx_global] = 1 if votos_1 > votos_0 else 0
    return predicciones, probabilidades

def calcular_metricas(Y_real, predicciones, probabilidades, nombre):
    probabilidades = np.asarray(probabilidades)
    return{
        "Modelo": nombre,
        "N prueba": int(len(Y_real)),
        "Exactitud": float(accuracy_score(Y_real, predicciones)),
        "Exactitud balanceada": float(balanced_accuracy_score(Y_real, predicciones)),
        "Precision clase 1": float(precision_score(Y_real, predicciones, pos_label=1, zero_division=0)),
        "Recall clase 1": float(recall_score(Y_real, predicciones, pos_label=1, zero_division=0)),
        "F1 clase 1": float(f1_score(Y_real, predicciones, pos_label=1, zero_division=0)),
        "F1 macro": float(f1_score(Y_real, predicciones, average="macro", zero_division=0)),
        "AUC ROC": (float(roc_auc_score(Y_real, probabilidades[:, 1])) if np.unique(Y_real).size == 2 else np.nan)
    }

def crear_grafica_clases(Y):
    frecuencias = pd.Series(Y).value_counts().reindex([0, 1], fill_value=0)
    figura, eje = plt.subplots(figsize=(8,5))
    barras = eje.bar(["Gana jugador 2", "Gana jugador 1"], [frecuencias.loc[0], frecuencias.loc[1]])
    eje.set_title("Distribucion de la variable objetivo")
    eje.set_ylabel("Numero de partidas")
    for barra, cantidad in zip(barras, [frecuencias.loc[0], frecuencias.loc[1]]):
        eje.annotate(f"{cantidad:,}", (barra.get_x() + barra.get_width() / 2, barra.get_height()), ha="center", va="bottom", xytext=(0, 3), textcoords="offset points")
    figura.tight_layout()
    figura.savefig(RESULTADOS_DIR / "distribucion_clases.png", dpi=160, bbox_inches="tight")
    plt.close(figura)

def crear_grafica_matrices_confusion(matriz_sklearn, matriz_propio):
    figura, ejes = plt.subplots(1, 2, figsize=(13, 5.5))
    titulos = ["KNN scikit-learn", "KNN implementacion propia"]
    for eje, matriz, titulo in zip(ejes, [matriz_sklearn, matriz_propio], titulos):
        imagen = eje.imshow(matriz, interpolation="nearest")
        eje.set(xticks=[0, 1], yticks=[0, 1], xticklabels=["Predice gana J2", "Predice gana J1"], yticklabels=["Real gana J2", "Real gana J1"], xlabel="Clase predicha", ylabel="Clase real", title=titulo)
        eje.tick_params(axis="x", rotation=10)
        umbral = matriz.max() / 2 if matriz.size else 0
        for fila in range(2):
            for columna in range(2):
                eje.text(columna, fila, f"{matriz[fila, columna]:,}", ha="center", va="center", color="white" if matriz[fila, columna] > umbral else "black", fontsize=11)
        figura.colorbar(imagen, ax=eje, fraction=0.046, pad=0.04)
    figura.suptitle("Comparacion de matrices de confusion en el conjunto de prueba")
    figura.tight_layout()
    figura.savefig(RESULTADOS_DIR / "comparacion_matrices_confusion.png", dpi=160, bbox_inches="tight")
    plt.close(figura)

def crear_grafica_validacion(resultados):
    figura, eje = plt.subplots(figsize=(9, 6))
    for ponderacion in PONDERACIONES:
        subconjunto = (resultados[resultados["param_knn__weights"] == ponderacion].copy().assign(k=lambda df: df["param_knn__n_neighbors"].astype(int)).sort_values("k"))
        eje.plot(subconjunto["k"], subconjunto["mean_test_score"], marker="o", label=f"Pesos: {ponderacion}")
        
    eje.set_title("Seleccion de K mediante validacion cruzada")
    eje.set_xlabel("Numero de vecinos (K)")
    eje.set_ylabel("F1 macro medio en validacion")
    eje.set_xticks(sorted(resultados["param_knn__n_neighbors"].astype(int).unique()))
    eje.legend()
    figura.tight_layout()
    figura.savefig(RESULTADOS_DIR / "seleccion_k_validacion.png", dpi=160, bbox_inches="tight")
    plt.close(figura)

def evaluar_modelo(datos_modelo):
    imprimir_titulo("SEPARACION DE DATOS EN ENTRENAMIENTO Y PRUEBA")
    X = datos_modelo[VARIABLES_PREDICTORAS]
    Y = datos_modelo[VARIABLE_OBJETIVO].astype(int)
    conteo_clases = Y.value_counts()

    if len(datos_modelo) < MINIMO_FILAS_MODELO:
        raise ValueError(f"Solo quedaron {len(datos_modelo)} partidas; se requieren al menos {MINIMO_FILAS_MODELO}.")
    if conteo_clases.min() < 10:
        raise ValueError(f"Una clase tiene muy pocas observaciones para separar y validar el modelo: {conteo_clases.to_dict()}")

    indices_entrenamiento, indices_prueba = train_test_split(datos_modelo.index, test_size=PROPORCION_PRUEBA, random_state=SEMILLA_ALEATORIA, stratify=Y)
    X_entrenamiento, X_prueba = X.loc[indices_entrenamiento], X.loc[indices_prueba]
    y_entrenamiento, y_prueba = Y.loc[indices_entrenamiento].to_numpy(dtype=int), Y.loc[indices_prueba].to_numpy(dtype=int)
    print(f"Partidas para entrenamiento: {len(X_entrenamiento):,} ({1 - PROPORCION_PRUEBA:.0%})")
    print(f"Partidas para prueba: {len(X_prueba):,} ({PROPORCION_PRUEBA:.0%})")
    print("La separacion es algo planeado. Un mismo jugador puede aparecer en partidas de ambos conjuntos; ya se documento como limitacion.")
    
    if int(pd.Series(y_entrenamiento).value_counts().min()) < NUMERO_PARTICIONES_CV:
        raise ValueError("No hay suficientes ejemplos de cada clase para la validacion cruzada.")

    imprimir_titulo("SELECCION DE K PARA KNN DE SCIKIT-LEARN")
    pipeline = crear_pipeline_knn()
    cv = StratifiedKFold(n_splits=NUMERO_PARTICIONES_CV, shuffle=True, random_state=SEMILLA_ALEATORIA)
    maximo_k_por_pliegue = len(X_entrenamiento) - int(np.ceil(len(X_entrenamiento) / NUMERO_PARTICIONES_CV))
    valores_k_validos = [k for k in VALORES_K if k <= maximo_k_por_pliegue]
    if not valores_k_validos:
        raise ValueError(f"El conjunto de entrenamiento es demasiado pequennio para los valores de K configurados con {NUMERO_PARTICIONES_CV} pliegues. El maximo K admisible es {maximo_k_por_pliegue}.")
    busqueda = GridSearchCV(estimator=pipeline, param_grid={"knn__n_neighbors": valores_k_validos, "knn__weights": PONDERACIONES}, scoring="f1_macro", cv=cv, n_jobs=N_JOBS_CV, pre_dispatch="2*n_jobs", refit=True, return_train_score=False, error_score="raise")
    busqueda.fit(X_entrenamiento, y_entrenamiento)
    resultados_cv = (pd.DataFrame(busqueda.cv_results_)[["rank_test_score", "param_knn__n_neighbors", "param_knn__weights", "mean_test_score", "std_test_score"]].sort_values(["rank_test_score", "param_knn__n_neighbors"]))
    resultados_cv.to_csv(RESULTADOS_DIR / "resultados_validacion_cruzada.csv", index=False, encoding="utf-8-sig")
    imprimir_tabla(resultados_cv.round(5))
    mejor_k = int(busqueda.best_params_["knn__n_neighbors"])
    mejores_pesos = str(busqueda.best_params_["knn__weights"])
    print(f"\nMejor configuracion seleccionada: K={mejor_k}, weights='{mejores_pesos}'")
    print(f"F1 macro medio en validacion cruzada: {busqueda.best_score_:.5f}")
    imprimir_titulo("COMPARACION EN EL CONJUNTO DE PRUEBA")
    modelo_sklearn = busqueda.best_estimator_
    pred_sklearn = modelo_sklearn.predict(X_prueba)
    prob_sklearn = modelo_sklearn.predict_proba(X_prueba)
    clases_sklearn = list(modelo_sklearn.named_steps["knn"].classes_)
    
    if clases_sklearn != [0, 1]:
        raise ValueError(f"Se esperaba la codificacion de clases binarias, pero se obtuvo {clases_sklearn}.")

    preprocesador_ajustado = modelo_sklearn.named_steps["preparacion"]
    pred_propio, prob_propio = knn_propio(preprocesador_ajustado.transform(X_entrenamiento), y_entrenamiento, preprocesador_ajustado.transform(X_prueba), k=mejor_k, ponderacion=mejores_pesos)
    base = DummyClassifier(strategy="most_frequent")
    base.fit(X_entrenamiento, y_entrenamiento)
    pred_base = base.predict(X_prueba)
    prob_base = base.predict_proba(X_prueba)
    metricas = pd.DataFrame([calcular_metricas(y_prueba, pred_sklearn, prob_sklearn, "KNN scikit-learn"), calcular_metricas(y_prueba, pred_propio, prob_propio, "KNN propio"), calcular_metricas(y_prueba, pred_base, prob_base, "Clasificador base (clase mayoritaria)")])
    imprimir_tabla(metricas.round(5))
    metricas.to_csv(RESULTADOS_DIR / "metricas_comparacion_knn.csv", index=False, encoding="utf-8-sig")
    matriz_sklearn = confusion_matrix(y_prueba, pred_sklearn, labels=[0, 1])
    matriz_propio = confusion_matrix(y_prueba, pred_propio, labels=[0, 1])
    matriz_base = confusion_matrix(y_prueba, pred_base, labels=[0, 1])
    pd.DataFrame([{"Modelo": nombre, "Real_0_Pred_0": int(m[0, 0]), "Real_0_Pred_1": int(m[0, 1]), "Real_1_Pred_0": int(m[1, 0]), "Real_1_Pred_1": int(m[1, 1])} for nombre, m in [("KNN scikit-learn", matriz_sklearn), ("KNN propio", matriz_propio), ("Clasificador base", matriz_base)]]).to_csv(RESULTADOS_DIR / "matrices_confusion.csv", index=False, encoding="utf-8-sig")
    crear_grafica_matrices_confusion(matriz_sklearn, matriz_propio)
    acuerdo = float(np.mean(pred_sklearn == pred_propio))
    diferencias = int(np.sum(pred_sklearn != pred_propio))
    print(f"\nCoincidencia de predicciones entre implementaciones: {acuerdo:.4%}")
    print(f"Predicciones diferentes entre ambas implementaciones: {diferencias:,} de {len(y_prueba):,}")
    predicciones = datos_modelo.loc[X_prueba.index, ["id_partida", "jugador_1_uuid", "jugador_2_uuid", "elo_previo_jugador_1_estimado", "elo_previo_jugador_2_estimado", VARIABLE_OBJETIVO]].rename(columns={VARIABLE_OBJETIVO: "clase_real"}).assign(prediccion_sklearn=pred_sklearn, probabilidad_sklearn_victoria_jugador_1=prob_sklearn[:, clases_sklearn.index(1)], prediccion_knn_propio=pred_propio, probabilidad_propia_victoria_jugador_1=prob_propio[:, 1], prediccion_base=pred_base)
    predicciones.to_csv(RESULTADOS_DIR / "predicciones_prueba_knn.csv", index=False, encoding="utf-8-sig")
    pd.concat([pd.DataFrame(classification_report(y_prueba, pred_sklearn, labels=[0, 1], target_names=["Gana jugador 2", "Gana jugador 1"], output_dict=True, zero_division=0)).T.assign(Modelo="KNN scikit-learn"), pd.DataFrame(classification_report(y_prueba, pred_propio, labels=[0, 1], target_names=["Gana jugador 2", "Gana jugador 1"], output_dict=True, zero_division=0)).T.assign(Modelo="KNN propio")]).to_csv(RESULTADOS_DIR / "reporte_por_clase.csv", encoding="utf-8-sig")
    crear_grafica_clases(Y)
    crear_grafica_validacion(pd.DataFrame(busqueda.cv_results_))
    print("\nArchivos generados:")
    for nombre in ["datos_modelo_knn.csv", "distribucion_clases.csv", "resultados_validacion_cruzada.csv", "metricas_comparacion_knn.csv", "matrices_confusion.csv", "reporte_por_clase.csv", "predicciones_prueba_knn.csv", "distribucion_clases.png", "seleccion_k_validacion.png", "comparacion_matrices_confusion.png"]:
        print(f"  - {RESULTADOS_DIR / nombre}")
    return {
        "metricas": metricas,
        "mejor_k": mejor_k,
        "mejores_pesos": mejores_pesos,
        "f1_cv": float(busqueda.best_score_),
        "acuerdo_implementaciones": acuerdo,
        "predicciones_diferentes": diferencias,
        "n_prueba": len(y_prueba),
        "n_entrenamiento": len(y_entrenamiento)
    }

def ejecutar_act6():
    with registrar_salida(REPORTE_TXT):
        imprimir_titulo("ACTIVIDAD 6 - CLASIFICACION DE RESULTADOS CON KNN")
        print(f"Directorio base: {BASE_DIR}")
        print(f"Directorio de resultados: {RESULTADOS_DIR}")
        print(f"Proporcion entrenamiento/prueba: {1 - PROPORCION_PRUEBA:.0%}/{PROPORCION_PRUEBA:.0%}")
        print(f"Semilla aleatoria: {SEMILLA_ALEATORIA}")
        print(f"Particiones de validacion cruzada: {NUMERO_PARTICIONES_CV}")
        print(f"Procesos maximos para la validacion: {N_JOBS_CV}")
        print(f"Valores K evaluados: {VALORES_K}")
        print(f"Ponderaciones evaluadas: {PONDERACIONES}")
        print(f"Predictores numericos: {VARIABLES_NUMERICAS}")
        print(f"Predictores categoricos: {VARIABLES_CATEGORICAS}")
        try:
            partidas, jugadores, cambios = cargar_tablas()
            mostrar_calidad(partidas, jugadores, cambios)
            datos_modelo = construir_dataset_modelo(partidas, jugadores, cambios)
            resultados = evaluar_modelo(datos_modelo)
        except Exception as error:
            imprimir_titulo("ERROR DURANTE LA EJECUCION")
            print(f"Tipo de error: {type(error).__name__}")
            print(f"Descripcion: {error}")
            print("\nNo se considera completada la ejecucion. Revise el error y los archivos de entrada.")
            print(f"Reporte de ejecucion: {REPORTE_TXT}")
            raise
        imprimir_titulo("RESUMEN FINAL")
        print(f"Partidas de modelado: {len(datos_modelo):,}")
        print(f"Mejor K: {resultados['mejor_k']}")
        print(f"Ponderacion: {resultados['mejores_pesos']}")
        print(f"F1 macro medio en validacion cruzada: {resultados['f1_cv']:.5f}")
        print(f"Coincidencia entre KNN scikit-learn y KNN propio: {resultados['acuerdo_implementaciones']:.4%}")
        print(f"\nCONSIDERACIONES")
        print("\tELO: El elo previo a la partida es una estimacion construida a partir de los datos poseidos.")
        print("Particiones: Las partidas estan separadas por fila, no por jugador. Por lo que, un mismo jugador puede aparecer en entrenamiento y prueba.")
        print(f"\nReporte completo: {REPORTE_TXT}")
        print(f"Directorio de resultados: {RESULTADOS_DIR}")

if __name__ == "__main__":
    ejecutar_act6()
