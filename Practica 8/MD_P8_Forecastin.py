"""
████████████████████████████████████████████████████████████████████████████
█  ACTIVIDAD 8 - PRONOSTICO DE ACTIVIDAD Y COMPOSICION DE PARTIDAS         █
████████████████████████████████████████████████████████████████████████████

-------------------------------------------------------------------------->
DESCRIPCION GENERAL DEL PROGRAMA
-------------------------------------------------------------------------->

    Esta practica consisten en analizar la evolucion temporal de la
    actividad de MCSR Ranked, temporada 10, mediante un modelo de regresion
    lineal multiple aplicado a una serie de tiempo com frecuencia horaria.
    Para ello, se utilizaron las tablas de partidas.csv y 
    data_clustering_asignados.csv, el cual fue generado durante la Actividad
    7, la cual contiene las etiquetas de los grupos identificados mediante
    K-Means.

    Se tiene como objetivo principal el estimar la cantidad de partidas por
    hora, y analizar la composicion de la actividad mediante la cantidad
    de partidas pertenecientes a cada uno de los dos clusters 
    identificados previamente. Para lo cual se ajustan tres modelos
    independientes de regresion lineal, donde cada uno utiliza una tendencia
    temporal y dos componentes ciclicos para representar las variaciones
    asociadas a la hora del día.

    Como salida esperada son tablas CSV, graficas de exploracion, validacion,
    residuos y pronostico, asi como un reporte TXT con los principales 
    resultados y consideraciones del analisis.

-------------------------------------------------------------------------->
MODELO DE PRONOSTICO: REGRESION LINEAL MULTIPLE
-------------------------------------------------------------------------->

    Unidad de analisis:
        ->  Una observacion representa un intervalo de una hora
        ->  La variable objetivo corresponde a la cantidad de partidas
            registradas durante ese intervalo
    Variables objetivo:
        ->  partidas_totales: Cantidad de partidas registradas por hora
        ->  partidas_cluster_0: Cantidad de partidas clasificadas en el
            cluster 0
        ->  partidas_cluster_1: Cantidad de partidas clasificadas en el
            cluster 1
    Predictores temporales:
        ->  Horas transcurridas desde el inicio del periodo
        ->  Seno de la hora del dia
        ->  Coseno de la hora del dia
    
    Los componenetes ciclicos se construyen mediante:
        seno = sin(2 * pi * h / 24)
        coseno = cos(2 * pi * h / 24)
        ; donde h representa la hora del día
        
        La representacion ciclica permitira modelar la continuidad entre
        las horas cercanas al inicio y al final del dia, evitando tratarlas
        como posiciones completamente independientemente.

    El modelo general se representa:
        Y_t = b0 + b1*t + b2*sin(2*pi*h/24) + b3*cos(2*pi*h/24) + error
    ; donde:
        ->  Y_t: cantidad de partidas estimada en el intervalo
        ->  t: horas transcurridas desde el inicio del periodo
        ->  h: hora del dia
        ->  b0: intercepto
        ->  b1: coeficiente de tendencia temporal
        ->  b2 y b3: coeficientes de los componentes ciclicos
        ->  error: diferencia entre el valor real y el estimado

-------------------------------------------------------------------------->
JUSTIFICACION DE DECISIONES TOMADAS
-------------------------------------------------------------------------->    

    ->  Se acorto este reporte por falta de tiempo, solo conservando las
        partes importantes. Se ha ido modificando con el tiempo, pero a
        este punto se priorizan las secciones que se consideran mas
        esenciales

    ->  Se utiliza una frecuencia horaria porque el periodo disponible 
        contiene solamente tres dias completos, agrupar por dia producira
        muy pocas observaciones para realizar una evaluacion razonable

    ->  Se exluyen el 26 y el 30 de abril porque representan los extremos
        de la extraccion.

    ->  Se utilizan los dias 27, 28 y 29 de abril, ya que son los dias
        dentro del dataset que proporcionan 72 intervalos horarios para
        construir la serie temporal.

    ->  Se incorporaron seno y coseno de la hora porque la actividad puede
        presentar variaciones dentro del dia, y estos pueden representar
        la naturaleza ciclica de las horas sin introducir una discontinuidad
    
    ->  Se utiliza regresion lineal multiple porque esta permite representar
        una tendencia temporal y variaciones horarias mediante una
        estructura relativamente sencilla e interpretable. 

    ->  Se hace una separacion cronologica cercana al 80/20, para los
        intervalor disponibles se utilizan 58 para entrenamiento y 14 de
        prueba; esto permite evaluar el comportamiento del modelo sobre
        observaciones peostriores a las utilizadas durante el ajuste

    ->  Se utilizan MAE y RMSE para medir la magnitud de los errores, R2
        para evaluar la variabilidad explicada, el error medio para
        identificar tendencias de subestimacion o sobreestimacion y MAPE
        para expresar el error porcentual

    ->  Se evalua la composicion procentual por separado, porque un modelo
        puede estimar cantidades razonables sin reproducir correctamente la
        distribucion entre los grupos.

    ->  Se reajustan los modelo finales con las 72 observaciones para generar
        el pronostico; la evaluacion de prueba se conserva por separado
        para no confundir los resultados de validacion con las estimaciones
        futuras

    ->  El horizonte se limita a seis hora por la reducida profundidad 
        temporal presente, las estimaciones solo representan una continuacion
        hipotetica del comporatamiento historico de la temporada 10. 

-------------------------------------------------------------------------->
INTERPRETACION DE RESULTADOS
-------------------------------------------------------------------------->

    De las 50,000 partidas validas y 23,842 registros con etiquetas de 
    K-Means, se utilizaron 48,040 partidas correspondientes a los tres 
    dias completos. Respecto a la serie resultante contiene 72 intervalos 
    horarios, de los cuales 58 se utilizaron para entrenamiento y 14 para 
    prueba.

    En la evaluacion de los modelos, la actividad total obtuvo un MAE
    de 49.58 partidas por hora, un RMSE de 57.4687 y un R2 de 0.7810;
    representando un ajuste favorable durante el periodo de prueba,
    aunque debe interpretarse considerando el reducido numero de
    observaciones disponibles. El modelo del cluster 0 obtuvo un MAE 
    de 38.6977 y un R2 de 0.0817; demostrando una capacidad limitada para 
    representar sus variaciones horarias. Por su parte, el cluster 1 
    obtuvo un MAE de 16.7178 y unR2 de 0.5783]; presentando un comportamiento
    que catalogaria como intermedio.

    El analisis de residuos mostro errores medios positivos en los tres
    modelos; indicando una tendencia general a subestimar las cantidades
    reales durante las horas de prueba. En la evaluacion porcentual, 
    la cobertura real media fue de 49.866%, mientras que la estimada fue de 
    47.3231%, con un MAE de 3.2554 puntos porcentuales. La participacion real
    media del cluster 0 fue de 46.6071%, mientras que la estimada fue de 
    43.4294%. Para el cluster 1 se obtuvo una participacion real de 53.3929% 
    y una estimada de 56.5706%. Ambos indicadores presentaron un MAE de 4.852 
    puntos porcentuales.

    Revisando las horas de prueba se observo que la participacion real del 
    cluster 0 aumento durante la segunda mitad del 29 de abril y modelo no 
    pudo reproducir por ompletamente este cambio, por lo que sus
    estimaciones porcentuales presentan errores mayores hacia el final
    del periodo evaluado.

    Los modelos se reajustaron con las 72 observaciones para
    estimar las siguientes seis horas, iniciando el 30 de abril a las
    01:00 UTC, despues del ultimo intervalo parcialmente observado. La cobertura
    media pronosticada de clasificacion fue de 53.00%, frente al 47.88% observado 
    durante el periodo modelado; esta diferencia representa una estimacion del 
    modelo y no demuestra que la cobertura realmente hubiera aumentado.

    En si, la actividad total presenta el mejor comportamiento predictivo 
    obtenido, mientras que la composicion de los clusters muestra limitaciones 
    para reproducir satisfactoriamente los cambios buscos de los horarios.
"""

from pathlib import Path
from contextlib import contextmanager
import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
"""
████████████████████████████████████████████████████████████████████████████
█  CONSTANTES Y RUTAS DE ARCHIVOS                                          █
████████████████████████████████████████████████████████████████████████████
"""
PROPORCION_ENTRENAMIENTO = 0.80
HORAS_PRONOSTICO = 6
EXCLUIR_DIAS_EXTREMOS = True
MINIMO_OBSERVACIONES = 24
COLUMNA_FECHA = "fecha_partida"
ARCHIVO_PARTIDAS = Path("data/final/main/partidas.csv")
ARCHIVO_CLUSTERING = Path("Act_7/resultados/datos_clustering_asignados.csv")
CARPETA_RESULTADOS = Path("Act_8/resultados_ejecucion")
CARPETA_CSV = CARPETA_RESULTADOS / "csv"
CARPETA_GRAFICAS = CARPETA_RESULTADOS / "graficas"
OBJETIVOS_CONFIG = {
    "partidas_totales": {"nombre": "Actividad total", "columna": "partidas_totales"}, 
    "partidas_cluster_0": {"nombre": "Partidas del cluster 0", "columna": "partidas_cluster_0"}, 
    "partidas_cluster_1": {"nombre": "Partidas del cluster 1", "columna": "partidas_cluster_1"}}
ARCHIVOS_CSV = {
    "resumen_calidad.csv": "calidad",
    "resumen_diario_cobertura.csv": "resumen_diario",
    "serie_horaria.csv": "serie",
    "metricas_regresion.csv": "metricas_regresion",
    "predicciones_prueba.csv": "pruebas",
    "resumen_residuos.csv": "resumen_residuos",
    "metricas_composicion_prueba.csv": "metricas_composicion",
    "evaluacion_composicion_prueba.csv": "detalle_composicion",
    "pronostico_6_horas.csv": "pronostico"}
ARCHIVOS_GRAFICAS = [
    "actividad_horaria.png", "composicion_clusters_horaria.png",
    "porcentaje_clusters_horaria.png", "validacion_actividad.png",
    "validacion_cluster_0.png", "validacion_cluster_1.png",
    "residuos_actividad.png", "residuos_cluster_0.png",
    "residuos_cluster_1.png", "pronostico_actividad.png",
    "pronostico_composicion.png", "cobertura_clusters.png",
    "validacion_cobertura_prueba.png", "validacion_participacion_clusters_prueba.png"]

def mape(reales, predicciones):
    errores = np.divide(np.abs(reales - predicciones), np.abs(reales), out=np.full(len(reales), np.nan, dtype=float), where=np.abs(reales) > 0)
    return float(np.nanmean(errores) * 100) if np.isfinite(errores).any() else np.nan

METRICAS_CALCULADORAS = {
    "MAE": lambda r, p: float(mean_absolute_error(r, p)),
    "RMSE": lambda r, p: float(np.sqrt(mean_squared_error(r, p))),
    "R2": lambda r, p: float(r2_score(r, p)) if np.unique(r).size > 1 else np.nan,
    "Error_Medio": lambda r, p: float(np.mean(r - p)),
    "MAPE_pct": lambda r, p: float(np.nanmean(np.abs((r - p) / np.where(r > 0, r, np.nan))) * 100.0),
    "MAPE_pct": mape}

"""
████████████████████████████████████████████████████████████████████████████
█  FUNCIONES GENERALES Y REGISTRO DE SALIDA EN CONSOLA Y ARCHIVO TXT       █
████████████████████████████████████████████████████████████████████████████
"""
imprimir_titulo = lambda texto, ancho=100: print(f"\n{'█'*ancho}\n█{texto.upper().center(ancho - 2)}█\n{'█'*ancho}")

def imprimir_tabla(tabla, decimales=8):
    if not isinstance(tabla, pd.DataFrame):
        raise TypeError("???")
    if tabla.empty:
        print("(Sin registros para mostrar)")
        return
    df = tabla.copy()
    num_cols = set(df.select_dtypes(include="number").columns)
    if num_cols:
        df[list(num_cols)] = df[list(num_cols)].round(decimales)
    for col in df.select_dtypes(include="number").columns:
        df[col] = df[col].map(lambda v: "NaN" if pd.isna(v) else " ".join(str(v.get("nombre", v) if isinstance(v, dict) else v).split()))
    for col in num_cols:
        df[col] = df[col].map(lambda v: "NaN" if pd.isna(v) else str(v))
    encabezados = [" ".join(str(columna).split()) for columna in df.columns]
    filas = [[" ".join(str(v).split()) for v in f] for f in df.astype(object).where(df.notna(), "NaN").itertuples(index=False, name=None)]
    anchos = [max(len(col), max((len(fila[i]) for fila in filas), default=0)) for i, col in enumerate(encabezados)]
    es_nummerica = [columna in num_cols for columna in df.columns]
    separador = "+-" + "-+-".join("-" * ancho for ancho in anchos) + "-+"
    formatear_fila = lambda fila, enc=False: f"| {' | '.join(valor.rjust(anchos[i]) if es_nummerica[i] and not enc else valor.ljust(anchos[i]) for i, valor in enumerate(fila))} |"
    print(separador, formatear_fila(encabezados, True), separador, *(formatear_fila(f) for f in filas), separador, sep="\n")

class SalidaDuplicada:
    def __init__(self, salida_original, archivo):
        self.salida_original, self.archivo = salida_original, archivo

    def write(self, texto):
        self.salida_original.write(texto)
        self.archivo.write(texto)
        self.flush()
        return len(texto)

    def flush(self):
        self.salida_original.flush()
        self.archivo.flush()

@contextmanager
def registrar_salida(ruta):
    with open(ruta, "w", encoding="utf-8") as archivo:
        salida_original = sys.stdout
        sys.stdout = SalidaDuplicada(salida_original, archivo)
        try:
            yield
        finally:
            sys.stdout = salida_original

def resolver_base_dir():
    ubicacion, directorio_actual = Path(__file__).resolve().parent, Path.cwd()
    candidatos = list(dict.fromkeys([ubicacion, *ubicacion.parents, directorio_actual, *directorio_actual.parents]))
    archivos = [ARCHIVO_PARTIDAS, ARCHIVO_CLUSTERING]
    for candidato in candidatos:
        if all((candidato / archivo).is_file() for archivo in archivos):
            return candidato.resolve()
        if all((candidato / "MCSR_Ranked" / archivo).is_file() for archivo in archivos):
            return (candidato / "MCSR_Ranked").resolve()        
    raise FileNotFoundError("No se localizo la carpeta raiz de MCSR_Ranked ni los archivos CSV requeridos. Verifique la ubicacion del proyecto.")

def normalizar_id(serie): return pd.to_numeric(serie, errors="coerce").astype("Int64")

"""
████████████████████████████████████████████████████████████████████████████
█  CARGA, VALIDACION Y NORMALIZACION DE LOS DATOS                          █
████████████████████████████████████████████████████████████████████████████
"""
def convertir_fechas_utc(serie):
    texto = serie.astype("string").str.strip()
    numerico = pd.to_numeric(texto, errors="coerce")
    if float(numerico.notna().mean())>=0.90:
        magnitud = float(numerico.dropna().abs().median())
        unidad = "ns" if magnitud >= 1e17 else "us" if magnitud >= 1e14 else "ms" if magnitud >= 1e11 else "s"
        print(f"Formato de fecha detectado: marca de tiempo numérica ({unidad}).")
        return pd.to_datetime(numerico, unit=unidad, utc=True, errors="coerce")
    print("Formato de fecha detectado: texto/fecha interpretable; se normaliza a UTC.")
    return pd.to_datetime(texto, utc=True, errors="coerce")

def validar_claves_unicas(tabla, nombre, claves):
    if faltantes := [col for col in claves if col not in tabla.columns]:
        raise ValueError(f"La tabla {nombre} no contiene las columnas clave requeridas: {faltantes}")
    incompletas = tabla[claves].isna().any(axis=1)
    n_incompletas = int(incompletas.sum())
    completas_df = tabla[~incompletas]
    duplicadas = completas_df.duplicated(subset=claves, keep=False) if not completas_df.empty else pd.Series(False, index=completas_df.index)
    n_duplicadas = int(duplicadas.sum())
    print(f"{nombre:24} filas con clave incompleta: {n_incompletas:>8,}")
    print(f"{'':24} filas con clave duplicada: {n_duplicadas:>8,}")
    if n_incompletas:
        print(f"CONSIDERACION: Las claves incompletas de {nombre} no se usarán en sus relaciones.")
    if n_duplicadas:
        muestras = completas_df.loc[duplicadas, claves].head(10)
        raise ValueError(f"La tabla {nombre} contiene claves completas duplicadas: {claves}.\nFilas duplicadas: {n_duplicadas}.\n{muestras.to_string(index=False)}")
    return {"incompletas": n_incompletas, "duplicadas": n_duplicadas}

def cargar_dataset(ruta, nombre, columnas):
    if not ruta.is_file():
        raise FileNotFoundError(f"No se encontró el archivo {nombre}: {ruta}")
    disponibles = pd.read_csv(ruta, nrows=0, encoding="utf-8-sig").columns.tolist()
    if faltantes := [col for col in columnas if col not in disponibles]:
        raise ValueError(f"Faltan columnas en {nombre}: {faltantes}")
    tabla = pd.read_csv(ruta, usecols=columnas, encoding="utf-8-sig", low_memory=False)
    print(f"Archivo: {ruta}\n{nombre:24} {len(tabla):>10,} filas | {len(tabla.columns):>3} columnas")
    return tabla

def cargar_tablas(base_dir):
    config_datasets = {
        "partidas": {"ruta": base_dir / ARCHIVO_PARTIDAS, "columnas": ["id_partida", COLUMNA_FECHA], "claves": ["id_partida"], "transformar": lambda df: df.assign(id_partida=normalizar_id(df["id_partida"]), fecha_utc=convertir_fechas_utc(df[COLUMNA_FECHA]))},
        "datos_clustering_asignados": {"ruta": base_dir / ARCHIVO_CLUSTERING, "columnas": ["id_partida", "cluster"], "claves": ["id_partida"], "transformar": lambda df: df.assign(id_partida=normalizar_id(df["id_partida"]), cluster=pd.to_numeric(df["cluster"], errors="coerce").astype("Int64"))}
    }
    tablas = {}
    imprimir_titulo("ARCHIVOS DE ENTRADA")
    for nombre, cfg in config_datasets.items():
        tabla = cargar_dataset(cfg["ruta"], nombre, cfg["columnas"])
        tablas[nombre] = cfg["transformar"](tabla)
    imprimir_titulo("VALIDACION DE CLAVES")
    for nombre, cfg in config_datasets.items():
        validar_claves_unicas(tablas[nombre], nombre, cfg["claves"])
    fechas_v = tablas["partidas"]["fecha_utc"].dropna()
    if not fechas_v.empty and (fechas_v.dt.hour * 3600 + fechas_v.dt.minute * 60 + fechas_v.dt.second).nunique() == 1:
        raise ValueError(f"{COLUMNA_FECHA} no contiene horas válidas.")
    datos = tablas["partidas"].dropna(subset=["id_partida"]).merge(tablas["datos_clustering_asignados"].dropna(subset=["id_partida", "cluster"])[["id_partida", "cluster"]], on="id_partida", how="left", validate="one_to_one")
    etiquetas = sorted(datos["cluster"].dropna().astype(int).unique().tolist())
    if etiquetas != [0, 1]:
        raise ValueError(f"Se esperaban las etiquetas 0 y 1. Se econtraron: {etiquetas}")
    return datos, etiquetas

def mostrar_calidad(datos, etiquetas):
    resumen = [
        ("Partidas originales", len(datos)), ("Partidas con fecha valida", int(datos["fecha_utc"].notna().sum())), ("Partidas con fecha invalida", int(datos["fecha_utc"].isna().sum())), ("Partidas con etiqueta K-Means", int(datos["cluster"].notna().sum())), ("Partidas sin etiqueta K-Means", int(datos["cluster"].isna().sum())), 
        ("Etiquetas de K-Means", ", ".join(map(str, etiquetas)))
        ]
    tabla = pd.DataFrame(resumen, columns=["Indicador", "Valor"])
    imprimir_titulo("CALIDAD Y COBERTURA DE LOS DATOS")
    imprimir_tabla(tabla)
    return tabla

"""
████████████████████████████████████████████████████████████████████████████
█  CONSTRUCCION DE LA SERIE HORARIA                                        █
████████████████████████████████████████████████████████████████████████████
"""
def construir_serie_horaria(datos):
    datos_fecha = datos.dropna(subset=["fecha_utc"]).assign(fecha_dia=lambda df: df["fecha_utc"].dt.normalize())
    dias = pd.DatetimeIndex(sorted(datos_fecha["fecha_dia"].unique()), name="fecha")
    if len(dias) < 3:
        raise ValueError("No se tienen suficientes días.")
    dias_modelado = dias[1:-1] if EXCLUIR_DIAS_EXTREMOS else dias
    inicio, fin_exclusivo = dias_modelado[0], dias_modelado[-1] + pd.Timedelta(days=1) 
    indice = pd.date_range(inicio, fin_exclusivo - pd.Timedelta(hours=1), freq="h")
    periodo = datos_fecha.loc[(datos_fecha["fecha_utc"] >= inicio) & (datos_fecha["fecha_utc"] < fin_exclusivo)].copy().assign(fecha_hora=lambda df: df["fecha_utc"].dt.floor("h"))
    conteos_cluster = periodo.dropna(subset=["cluster"]).groupby(["fecha_hora", "cluster"]).size().unstack(fill_value=0)
    serie = (pd.DataFrame(index=indice)
        .assign(partidas_totales=periodo.groupby("fecha_hora").size().reindex(indice, fill_value=0).astype(int), partidas_cluster_0=conteos_cluster.get(0, pd.Series(dtype="int64")).reindex(indice, fill_value=0).astype(int), partidas_cluster_1=conteos_cluster.get(1, pd.Series(dtype="int64")).reindex(indice, fill_value=0).astype(int))
        .assign(
            partidas_clasificadas=lambda df: df["partidas_cluster_0"] + df["partidas_cluster_1"],
            partidas_sin_cluster=lambda df: df["partidas_totales"] - (df["partidas_cluster_0"] + df["partidas_cluster_1"]),
            cobertura_cluster_pct=lambda df: np.where(df["partidas_totales"] > 0, 100.0 * (df["partidas_cluster_0"] + df["partidas_cluster_1"]) / df["partidas_totales"], np.nan),
            porcentaje_cluster_0=lambda df: np.where((df["partidas_cluster_0"] + df["partidas_cluster_1"]) > 0, 100.0 * df["partidas_cluster_0"] / (df["partidas_cluster_0"] + df["partidas_cluster_1"]), np.nan))
        .assign(porcentaje_cluster_1=lambda df: 100.0 - df["porcentaje_cluster_0"]).reset_index(names="fecha_hora"))
    
    resumen_diario = (datos_fecha.groupby("fecha_dia").agg(primer_registro_utc=("fecha_utc", "min"), ultimo_registro_utc=("fecha_utc", "max"), partidas_totales=("id_partida", "size"), partidas_con_cluster=("cluster", "count")).reindex(dias, fill_value=0).reset_index()
        .assign(partidas_sin_cluster=lambda df: df["partidas_totales"] - df["partidas_con_cluster"], estado_periodo="INCLUIDO EN EL MODELADO", fecha=lambda df: df["fecha"].dt.strftime("%Y-%m-%d"),primer_registro_utc=lambda df: pd.to_datetime(df["primer_registro_utc"], utc=True).dt.strftime("%Y-%m-%d %H:%M:%S"),
            ultimo_registro_utc=lambda df: pd.to_datetime(df["ultimo_registro_utc"], utc=True).dt.strftime("%Y-%m-%d %H:%M:%S"))
    )
    if EXCLUIR_DIAS_EXTREMOS:
        resumen_diario.iloc[[0, -1], resumen_diario.columns.get_loc("estado_periodo")] = ["EXCLUIDO: PRIMER DÍA", "EXCLUIDO: ÚLTIMO DÍA"]
    imprimir_titulo("COBERTURA TEMPORAL Y SELECCIÓN DEL PERIODO")
    imprimir_tabla(resumen_diario, decimales=2)
    imprimir_titulo("MUESTRA DE LA SERIE HORARIA")
    imprimir_tabla(serie.head(12), decimales=2)
    return serie, resumen_diario, inicio

"""
████████████████████████████████████████████████████████████████████████████
█  REGRESION LINEAL Y EVALUACION                                           █
████████████████████████████████████████████████████████████████████████████
"""
def crear_predictores_temporales(fechas, inicio_modelado):
    fecha = pd.DatetimeIndex(pd.to_datetime(fechas, utc=True))
    horas_transcurridas = ((fecha - pd.to_datetime(inicio_modelado, utc=True)) / pd.Timedelta(hours=1)).to_numpy(dtype=float)
    hora_decimal = fecha.hour + fecha.minute / 60.0 + fecha.second / 3600.0
    angulo = 2.0 * np.pi * hora_decimal / 24.0
    return np.column_stack([horas_transcurridas, np.sin(angulo), np.cos(angulo)])

def evaluar_regresion_lineal(serie, columna, nombre, inicio_modelado):
    valores = pd.to_numeric(serie[columna], errors="coerce").to_numpy(dtype=float)
    cantidad = len(valores)
    if cantidad < MINIMO_OBSERVACIONES:
        raise ValueError(f"{nombre}: insuficientes observaciones.")
    corte = int(np.ceil(len(valores) * PROPORCION_ENTRENAMIENTO))
    fechas = pd.to_datetime(serie["fecha_hora"], utc=True)
    matriz_predictores = crear_predictores_temporales(fechas, inicio_modelado)
    modelo = LinearRegression().fit(matriz_predictores[:corte], valores[:corte])
    predicciones = modelo.predict(matriz_predictores[corte:])
    reales, residuos, absolutos = valores[corte:], valores[corte:] - predicciones, np.abs(valores[corte:] - predicciones)
    fecha_train, fecha_test = fechas.iloc[:corte], fechas.iloc[corte:]
    metricas = {
        "Variable": nombre, "Observaciones": cantidad, "Entrenamiento": corte, "Prueba": cantidad - corte, "Porcentaje_entrenamiento_real": 100 * corte / cantidad, "Inicio_entrenamiento_utc": fecha_train.iloc[0].strftime("%Y-%m-%d %H:%M"), "Fin_entrenamiento_utc": fecha_train.iloc[-1].strftime("%Y-%m-%d %H:%M"),
        "Inicio_prueba_utc": fecha_test.iloc[0].strftime("%Y-%m-%d %H:%M"), "Fin_prueba_utc": fecha_test.iloc[-1].strftime("%Y-%m-%d %H:%M"), "Coeficiente_tendencia_horas": float(modelo.coef_[0]), "Coeficiente_seno_hora": float(modelo.coef_[1]), "Coeficiente_coseno_hora": float(modelo.coef_[2]), "Intercepto": float(modelo.intercept_)
    }
    metricas.update({k: fn(reales, predicciones) for k, fn in METRICAS_CALCULADORAS.items()})
    detalle = pd.DataFrame({"fecha_hora": fecha_test.to_numpy(), f"real_{columna}": reales, f"pronosticado_{columna}": predicciones, f"pronosticado_redondeado_{columna}": np.rint(np.clip(predicciones, 0, None)).astype(int), f"error_{columna}": residuos, f"error_absoluto_{columna}": absolutos,
        f"error_porcentual_abs_{columna}": np.divide(absolutos, np.abs(reales), out=np.full(len(reales), np.nan), where=np.abs(reales) > 0) * 100
    })
    return modelo, metricas, detalle, corte

def resumir_residuos(pruebas):
    return pd.DataFrame([
        {
            "Variable": cfg["nombre"], "Observaciones_prueba": int(err.notna().sum()), "Error_medio": float(err.mean()), "Desviacion_estandar_error": float(err.std(ddof=1)), "Error_minimo": float(q[0.0]), "Primer_cuartil_error": float(q[0.25]), "Mediana_error": float(q[0.5]), "Tercer_cuartil_error": float(q[0.75]), 
            "Error_maximo": float(q[1.0]), "MAE": float(pruebas[f"error_absoluto_{col}"].mean()), "RMSE": float(np.sqrt(np.mean(err.to_numpy(dtype=float) ** 2))),
        } for col, cfg in OBJETIVOS_CONFIG.items() for err in [pruebas[f"error_{col}"]] for q in [err.quantile([0.0, 0.25, 0.5, 0.75, 1.0])]
    ])

def evaluar_composicion_porcentual(pruebas):
    columnas = ["real_partidas_totales", "real_partidas_cluster_0", "real_partidas_cluster_1", "pronosticado_redondeado_partidas_totales", "pronosticado_redondeado_partidas_cluster_0", "pronosticado_redondeado_partidas_cluster_1"]
    detalle = pd.DataFrame({"fecha_hora": pd.to_datetime(pruebas["fecha_hora"], utc=True)})
    for n, f in zip(("total_real", "c0_real", "c1_real", "total_estimado", "c0_estimado", "c1_estimado"), columnas):
        detalle[n] = pruebas[f].to_numpy(dtype=float)
    detalle["clasificadas_real"] = detalle["c0_real"] + detalle["c1_real"]
    detalle["clasificadas_estimadas"] = detalle["c0_estimado"] + detalle["c1_estimado"]
    config = {"cobertura": ("clasificadas_real", "clasificadas_estimadas", "total_real", "total_estimado"), "participacion_cluster_0": ("c0_real", "c0_estimado", "clasificadas_real", "clasificadas_estimadas"), "participacion_cluster_1": ("c1_real", "c1_estimado", "clasificadas_real", "clasificadas_estimadas")}
    metricas = []
    for nombre, (num_real, num_est, den_real, den_est) in config.items():
        real = np.divide(100 * detalle[num_real], detalle[den_real], out=np.full(len(detalle), np.nan), where=detalle[den_real].to_numpy() > 0)
        estimado = np.divide(100 * detalle[num_est], detalle[den_est], out=np.full(len(detalle), np.nan), where=detalle[den_est].to_numpy() > 0)
        detalle[f"{nombre}_real_pct"] = real
        detalle[f"{nombre}_estimada_pct"] = estimado
        residuo = real - estimado
        detalle[f"residuo_{nombre}_pp"] = residuo
        val = residuo[np.isfinite(residuo)]
        metricas.append({
            "Metrica": nombre.replace("_", " ").capitalize(), "Observaciones_prueba": int(np.isfinite(residuo).sum()), "Media_real_pct": float(np.mean(real[np.isfinite(real)])), "Media_estimada_pct": float(np.mean(estimado[np.isfinite(estimado)])),
            "Residuo_medio_real_menos_estimado_pp": float(np.mean(val)), "MAE_pp": float(np.mean(np.abs(val))), "RMSE_pp": float(np.sqrt(np.mean(val ** 2))), "Error_absoluto_maximo_pp": float(np.max(np.abs(val)))
        })
    detalle["coherencia_conteos_reales"] = np.where(detalle["clasificadas_real"] <= detalle["total_real"], "COHERENTE", "REVISAR")
    detalle["coherencia_conteos_estimados"] = np.where(detalle["clasificadas_estimadas"] <= detalle["total_estimado"], "COHERENTE", "REVISAR")
    return pd.DataFrame(metricas), detalle

def construir_pronostico_futuro(serie, ultimo_registro, inicio_modelado):
    fechas = pd.to_datetime(serie["fecha_hora"], utc=True)
    predictores = crear_predictores_temporales(fechas, inicio_modelado)
    modelos = {col: LinearRegression().fit(predictores, pd.to_numeric(serie[col], errors="coerce").to_numpy(dtype=float)) for col in OBJETIVOS_CONFIG}
    inicio_pronostico = max(fechas.max() + pd.Timedelta(hours=1), pd.to_datetime(ultimo_registro, utc=True).floor("h") + pd.Timedelta(hours=1))
    fechas_futuras = pd.date_range(inicio_pronostico, periods=HORAS_PRONOSTICO, freq="h")
    matriz_futura = crear_predictores_temporales(fechas_futuras, inicio_modelado)
    pronostico = pd.DataFrame({"fecha_hora": fechas_futuras}).assign(**{f"pronostico_{col}": np.rint(np.clip(modelo.predict(matriz_futura), 0, None)).astype(int) for col, modelo in modelos.items()})
    total = pronostico["pronostico_partidas_totales"]
    clasificadas = pronostico["pronostico_partidas_cluster_0"] + pronostico["pronostico_partidas_cluster_1"]
    dif = total - clasificadas
    pronostico = pronostico.assign(partidas_clasificadas_pronosticadas=clasificadas, diferencia_total_menos_clasificadas=dif, coherencia_conteos=np.where(dif >= 0, "COHERENTE", "REVISAR: CLASIFICADAS > TOTAL"), partidas_sin_cluster_pronosticadas=np.where(dif >= 0, dif, np.nan),
        cobertura_cluster_pronosticada_pct=np.divide(100 * clasificadas, total, out=np.full(len(pronostico), np.nan), where=total.to_numpy() > 0), porcentaje_cluster_0=100 * pronostico["pronostico_partidas_cluster_0"] / clasificadas.replace(0, np.nan),
        porcentaje_cluster_1=100 * pronostico["pronostico_partidas_cluster_1"] / clasificadas.replace(0, np.nan),
        variacion_cobertura_historica_pp=(np.divide(100 * clasificadas, total, out=np.full(len(pronostico), np.nan), where=total.to_numpy() > 0)) - (100 * float(serie["partidas_clasificadas"].sum()) / float(serie["partidas_totales"].sum()))
    )
    return pronostico, modelos, fechas.max(), pd.to_datetime(ultimo_registro, utc=True).floor("h"), inicio_pronostico, (100 * float(serie["partidas_clasificadas"].sum()) / float(serie["partidas_totales"].sum()))

def _generar_grafica(x_default, series_config, archivo_path, titulo, xlabel, ylabel, ylim=None, axvspan_info=None, vline=None, legend_ncol=1):
    fig, ax = plt.subplots(figsize=(11, 6))
    for item in series_config:
        label, x_data, y_data, style = (item if len(item) == 4 else (item[0], x_default, item[1], item[2]))
        ax.plot(x_data, y_data, label=label, **style)
    if axvspan_info:
        ax.axvspan(axvspan_info[0], axvspan_info[1], alpha=0.10, label=axvspan_info[2])
    if vline:
        ax.axvline(vline["0"], linestyle=vline.get("ls", "--"), linewidth=1, label=vline.get("label"))
    ax.set(title=titulo, xlabel=xlabel, ylabel=ylabel)
    if ylim: ax.set_ylim(ylim)
    ax.grid(alpha=0.25)
    ax.legend(ncol=legend_ncol)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(archivo_path, dpi=180, bbox_inches="tight")
    plt.close(fig)

def guardar_grafica_residuos(pruebas, columna, nombre, ruta):
    fig, ejes = plt.subplots(2, 1, figsize=(11, 8))
    fechas = pd.to_datetime(pruebas["fecha_hora"], utc=True)
    residuos, estimados = pruebas[f"error_{columna}"], pruebas[f"pronosticado_{columna}"]
    config_subtramas = [("plot", fechas, f"Residuos de prueba: {nombre}", "Fecha y hora (UTC)", {"marker": "o", "markersize": 3, "linewidth": 1}), ("scatter", estimados, "Residuos frente a valores estimados", "Partidas estimadas", {"alpha": 0.75, "edgecolors": "k", "linewidths": 0.5})]
    for ax, (metodo, x_data, titulo, xlabel, kwargs) in zip(ejes, config_subtramas):
        getattr(ax, metodo)(x_data, residuos, **kwargs)
        ax.axhline(0, linestyle="--", linewidth=1, color="gray")
        ax.set(title=titulo, xlabel=xlabel, ylabel="Real - estimado")
        ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(ruta, dpi=180, bbox_inches="tight")
    plt.close(fig)

def guardar_graficas(serie, pruebas, pronostico, detalle, resultados_graficas_dir):
    fechas, f_prueba, f_futura = pd.to_datetime(serie["fecha_hora"], utc=True), pd.to_datetime(pruebas["fecha_hora"], utc=True), pd.to_datetime(pronostico["fecha_hora"], utc=True)
    inicio_prueba, fin_prueba = f_prueba.min(), f_prueba.max() + pd.Timedelta(hours=1)

    _generar_grafica(fechas, [("Partidas reales", serie["partidas_totales"], {"marker": "o", "markersize": 3, "linewidth": 1})], resultados_graficas_dir / "actividad_horaria.png", "Actividad de MCSR Ranked por hora", "Fecha y hora", "Partidas",
        axvspan_info=(inicio_prueba, fin_prueba, "Periodo de prueba"), vline={"label": "Inicio de prueba", "0": inicio_prueba})
    _generar_grafica(fechas, [("Cluster 0", serie["partidas_cluster_0"], {"linewidth": 1}), ("Cluster 1", serie["partidas_cluster_1"], {"linewidth": 1})], resultados_graficas_dir / "composicion_clusters_horaria.png", "Composicion horaria de partidas clasificadas", "Fecha y hora", "Partidas")
    _generar_grafica(fechas, [("Cluster 0", serie["porcentaje_cluster_0"], {"linewidth": 1.2}), ("Cluster 1", serie["porcentaje_cluster_1"], {"linewidth": 1.2})], resultados_graficas_dir / "porcentaje_clusters_horaria.png", "Participacion porcentual historica de los clusters", "Fecha y hora", "Porcentaje", ylim=(0, 100))
    
    for col, nombre, arch in [("partidas_totales", "Actividad total", "validacion_actividad.png"), ("partidas_cluster_0", "Cluster 0", "validacion_cluster_0.png"), ("partidas_cluster_1", "Cluster 1", "validacion_cluster_1.png")]:
        _generar_grafica(fechas, [("Valor real", serie[col], {"linewidth": 1, "alpha": 0.65}), ("Predicción de prueba", f_prueba, pruebas[f"pronosticado_{col}"], {"marker": "o", "linestyle": "--", "linewidth": 1.3})], resultados_graficas_dir / arch, f"Validación cronologica: {nombre}", "Fecha y hora", "Partidas", 
            axvspan_info=(inicio_prueba, fin_prueba, "Periodo de prueba"), vline={"label": "Inicio de prueba", "0": inicio_prueba})
        guardar_grafica_residuos(pruebas, col, nombre, resultados_graficas_dir / f"residuos_{'actividad' if col == 'partidas_totales' else col.replace('partidas_', '')}.png")
        
    _generar_grafica(pd.to_datetime(detalle["fecha_hora"], utc=True), [("Cobertura real", detalle["cobertura_real_pct"], {"marker": "o"}), ("Cobertura estimada", detalle["cobertura_estimada_pct"], {"marker": "o", "linestyle": "--"})], resultados_graficas_dir / "validacion_cobertura_prueba.png", "Validacion de cobertura de clasificación", 
        "Fecha y hora", "Cobertura (%)", vline={"label": "Inicio de prueba", "0": inicio_prueba})
    _generar_grafica(pd.to_datetime(detalle["fecha_hora"], utc=True), [("Cluster 0 real", detalle["participacion_cluster_0_real_pct"], {"marker": "o"}), ("Cluster 0 estimado", detalle["participacion_cluster_0_estimada_pct"], {"marker": "o", "linestyle": "--"}), ("Cluster 1 real", detalle["participacion_cluster_1_real_pct"], 
        {"marker": "s"}), ("Cluster 1 estimado", detalle["participacion_cluster_1_estimada_pct"], {"marker": "s", "linestyle": "--"})], resultados_graficas_dir / "validacion_participacion_clusters_prueba.png", "Validacion de participacion porcentual de clusters", "Fecha y hora", "Participación (%)", 
        vline={"label": "Inicio de prueba", "0": inicio_prueba}, ylim=(0, 100), legend_ncol=2)
    historia = serie.loc[fechas >= f_futura.min() - pd.Timedelta(hours=24)]
    _generar_grafica(fechas, [("Actividad historica", pd.to_datetime(historia["fecha_hora"], utc=True), historia["partidas_totales"], {"marker": "o", "linewidth": 1}), ("Actividad pronosticada", f_futura, pronostico["pronostico_partidas_totales"], {"marker": "o", "linestyle": "--", "linewidth": 1.5})], 
        resultados_graficas_dir / "pronostico_actividad.png", f"Pronostico de actividad: siguientes {HORAS_PRONOSTICO} horas", "Fecha y hora", "Partidas", vline={"label": "Inicio del pronostico", "0": f_futura.min()})
    _generar_grafica(f_futura, [("Cluster 0", pronostico["porcentaje_cluster_0"], {"marker": "o"}), ("Cluster 1", pronostico["porcentaje_cluster_1"], {"marker": "o"})], resultados_graficas_dir / "pronostico_composicion.png", "Pronóstico de composición de partidas clasificadas", "Fecha y hora (UTC)", "Participación (%)", ylim=(0, 100))
    _generar_grafica(fechas, [("Cobertura historica", fechas, serie["cobertura_cluster_pct"], {"linewidth": 1}), ("Cobertura pronosticada", f_futura, pronostico["cobertura_cluster_pronosticada_pct"], {"marker": "o", "linestyle": "--"})], 
        resultados_graficas_dir / "cobertura_clusters.png", "Cobertura historica y pronosticada de K-Means", "Fecha y hora", "Cobertura (%)", vline={"label": "Inicio del pronostico", "0": f_futura.min()}, ylim=(0, 100))

def ejecutar_actividad():
    base_dir = resolver_base_dir()
    resultados_dir = base_dir / CARPETA_RESULTADOS
    csv_dir = base_dir / CARPETA_CSV
    graficas_dir = base_dir / CARPETA_GRAFICAS
    resultados_dir.mkdir(parents=True, exist_ok=True)
    csv_dir.mkdir(parents=True, exist_ok=True)
    graficas_dir.mkdir(parents=True, exist_ok=True)
    ruta_reporte = resultados_dir / "reporte_act8.txt"
    with registrar_salida(ruta_reporte):
        imprimir_titulo("ACTIVIDAD 8 - PRONÓSTICO DE ACTIVIDAD Y COMPOSICIÓN DE PARTIDAS")
        datos, etiquetas = cargar_tablas(base_dir)
        calidad = mostrar_calidad(datos, etiquetas)
        datos_fecha = datos.dropna(subset=["fecha_utc"])
        if datos_fecha.empty: raise ValueError("Fechas vacías.")
        imprimir_titulo("DISTRIBUCIÓN DIARIA ORIGINAL")
        imprimir_tabla(datos_fecha.groupby(datos_fecha["fecha_utc"].dt.strftime("%Y-%m-%d")).size().rename_axis("Fecha").reset_index(name="Partidas"))
        serie, resumen_diario, inicio_modelado = construir_serie_horaria(datos)
        metricas, pruebas, corte = [], None, None
        for col, nombre in OBJETIVOS_CONFIG.items():
            _, resumen, predicciones, c_actual = evaluar_regresion_lineal(serie, col, nombre, inicio_modelado)
            if corte and c_actual != corte: raise RuntimeError("Divisiones temporales discordantes.")
            corte = c_actual
            metricas.append(resumen)
            pruebas = predicciones if pruebas is None else pruebas.merge(predicciones, on="fecha_hora", how="inner", validate="one_to_one")
        metricas_regresion = pd.DataFrame(metricas)
        resumen_residuos = resumir_residuos(pruebas)
        metricas_composicion, detalle_composicion = evaluar_composicion_porcentual(pruebas)
        pronostico, modelos_finales, ultima_hora_modelada, ultima_hora_observada, inicio_pronostico, cobertura_historica = construir_pronostico_futuro(serie, datos_fecha["fecha_utc"].max(), inicio_modelado)
        imprimir_titulo("MÉTRICAS DE EVALUACIÓN")
        imprimir_tabla(metricas_regresion, decimales=4)
        imprimir_titulo("ANÁLISIS DE RESIDUOS Y ERRORES DE PRUEBA")
        imprimir_tabla(resumen_residuos, decimales=4)
        imprimir_titulo("EVALUACIÓN DE LA COMPOSICIÓN PORCENTUAL EN PRUEBA")
        imprimir_tabla(metricas_composicion, decimales=4)
        imprimir_tabla(detalle_composicion, decimales=2)
        imprimir_titulo("COHERENCIA Y COBERTURA DEL PRONÓSTICO")
        print(f"Inicio del pronostico: {inicio_pronostico:%Y-%m-%d %H:%M} UTC")
        print(f"Ultima hora modelada: {ultima_hora_modelada:%Y-%m-%d %H:%M} UTC")
        print(f"Ultima hora parcialmente observada: {ultima_hora_observada:%Y-%m-%d %H:%M} UTC")
        print(f"Cobertura histórica: {cobertura_historica:.2f}% | Media futura: {pronostico['cobertura_cluster_pronosticada_pct'].mean():.2f}%")
        imprimir_tabla(pronostico, decimales=2)
        tablas = {"calidad": calidad, "resumen_diario": resumen_diario, "serie": serie, "metricas_regresion": metricas_regresion, "pruebas": pruebas, "resumen_residuos": resumen_residuos, "metricas_composicion": metricas_composicion, "detalle_composicion": detalle_composicion, "pronostico": pronostico}
        archivos_csv = [t.to_csv(csv_dir / n, index=False, encoding="utf-8-sig") or (csv_dir / n) for n, c in ARCHIVOS_CSV.items() for t in [tablas[c]]]
        guardar_graficas(serie, pruebas, pronostico, detalle_composicion, graficas_dir)
        imprimir_titulo("RESUMEN FINAL")
        print(f"Partidas originales: {len(datos):,} | Intervalos modelados: {len(serie):,}")
        print(f"Entrenamiento: {corte} | Prueba: {len(pruebas)}")
        print(f"Regresiones ajustadas: {len(modelos_finales)}")
        print(f"Reporte: {ruta_reporte}")
        print(f"CSVs guardados en: {csv_dir}")
        print(f"Gráficas guardadas en: {graficas_dir}")

def main():
    try:
        ejecutar_actividad()
    except Exception as error:
        print(f"\nERROR DURANTE LA EJECUCION DE LA ACTIVIDAD 8: {type(error).__name__}: {error}", file=sys.stderr)
        raise

if __name__ == "__main__":
    main()