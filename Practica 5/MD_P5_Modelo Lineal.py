"""
████████████████████████████████████████████████████████████████████████████
█  MODELO LINEAL Y CORRELACIOAL - MCSR RANKED TEMPORADA 10                 █
████████████████████████████████████████████████████████████████████████████

------------------------------------------------>
DESCRIPCION GENERAL DE PROGRAMA
------------------------------------------------>
    El programa utiliza los datos finales de la practica 1 para estudiar la
    relacion entre el ELO estimado previo de una partida y el tiempo que
    tada un jugador en completar la partida. Para llevar a cabo dicho 
    analisis, se combinana los datos de completaciones y cambios de ELO
    mediante la clave compuesta formada por el identidicador de partida y 
    el identificador unico universal del jugado; como agregado se carga la
    tabla de los jugadores para revisar la calidad de datos y realizar una
    comparacion entre los campos de elo, meramente experimental.

    Una vez realizada la validacion de los datos y seleccion de observaciones
    utilizables para el analisis, se estuadia la asociacion entre ambas 
    variables mediante correlaciones y una regresion lineal. El analisis
    realiza una parte inferencial, destinada a estimar e interpretar la
    relacion lineal, y una evaluacion predictiva que comprueba el 
    comportamiento del modelo con jugadores que no aparecen en el conjunto
    de entrenamiento.

    Como salida el programa genera tablas de resultados, un archivo CSV
    con los datos utilizados, otro con las predicciones y residuos, genera
    graficas de apoyo y un reporte TXT con los resultados de su ejecucion
    y consideraciones del analisis.

------------------------------------------------>
MODELO LINEAL
------------------------------------------------>
    Variables de estudio:

        -> Variable respuesta (Y): Tiempo de completacion de la partida

        -> Variable explicativa (X): ELO previo estimado del jugador.

    El ELO previo se reconsturye mediante la expresion: 
        elo_previo_estimado = elo - cambio de elo

    Esta reconstruccion se utiliza como una estimacion de ELO anterior al 
    cambio registrado. Su interpretacion depende de la convencion temporal
    de los campos proporcionados por la fuente.

    La relacion que se debe estudiar se expresa mediante el siguiente
    modelo:

        tiempo = beta_0 + beta_1 + ELO_previo + error

    En donde:
        beta_0 = Valor estimado cuando el ELO es cero
        beta_1 = Cambio promedio estiamdo en el tiempo por cada punto 
                 de ELO
        error = diferencia entre el tiempo observado y el estiamdo por
                la recta
    
    La pendiente tambien se expresa por cada 100 puntos de ELO para 
    facilitar su interpretacion. Una pendiente negativa representa una
    asociacion lineal en los valores mayores de ELO se relacionan con 
    tiempos estimados menotes, en promedio. No demuestra que el ELO
    cause esa diferencia.

------------------------------------------------>
COMPONENTES DENTRO DEL ANALISIS 
------------------------------------------------>
    -> Analisis de calidad y preparacion:
        Se revisan los valores ausentes, datos no numericos, valor no finitos,
        claves duplicadas y la correspondencia entre las tablas. Se conservan 
        las observaciones con tiempo de completacion positivo y finito, ELO y
        cambio de ELO validos, y un ELO previo estimado positivo. Los datos
        que no cumplen con esto no se utilizan en el ajuste.

    -> Analisis de asociacion:
        Se calcula la correlacion de Pearson para estudiar la asociacion
        lineal  y la correlacion de Spearman para evaluar la asociacion 
        monotona a partir de los rangos. Ambas medidas son complementarias y
        no representan por so soloas una prueba de casualidad.

    -> Analisis Inferencial:
        Se ajusta una regresion lineal por minimos cuadrados ordinarios sobre 
        las observaciones validas. Para relizar el calculo de la incertidumbre
        de la pendiente se utilizan errores estandar robustos agrupados por
        jugador, debido a que un mismo jugador puede aparecer en varias
        partidas

    -> Evaluacion predictiva:
        Se divide el conjunto de datos por jugador, de forma en que las
        partidas de un mismo jugador no se pueden repartirse entre 
        entrenamiento y prueba. La recta predictiva se ajustan con el conjunto
        de entrenamiento y se evalua con los jugadores reservados para prueba.

    -> Evaluacion de errores:
        Se utiliza MAE, RMSE y R2 para medir el rendimiento predictivo. 
        Asi mismo, se genera una grafica de dispersion con la recta estiamda
        y una de los residuos para examinar los errores del modelo.

------------------------------------------------>
HIPOTESIS ESTADISTICAS
------------------------------------------------>

    Se considera un nivel de significancia de alfa = 0.05

    H0: la pendiente pobalcional de la relacion lineal ente el ELO previo 
        estimado y el tiempo de completacion es igual a cero.
        beta_1 = 0
    
    H1: La pendiente poblacional de la relacion lineal entre ambas variables
        es diferente de cero.
        beta_1 != 0

    Si el valor p es inferior a 0.05, se rechaza H0. Aportando evidencia estadistica
    de una asociacion lineal distinta de cero bajo los supuestos del analisis. El 
    resultado no implica casualidad ni garantiza que la relacion lineal describa por
    completo el comportamiento de los datos.

------------------------------------------------>
JUSTIFICACION DE DECISIONES TOMADAS
------------------------------------------------>

    ->  Se excluyen las observaciones con valores ausentes, no finitos, tiempos
        no positivos o ELO previo estiamdo no positivo, ya que no permiten realizar
        un analisis definido.
    
    ->  La regresion lineal permite estudiar la direccion y la magnitud de la 
        asociacion entre un variable explicativa y una numerica. La simplicidad
        permite interpretar directamente la pendiente y comparar las estimaciones
        con los datos

    ->  Se calculan errores estandar robustos agrupados por jugador en el analisis
        inferencial porque las partidas de un mismo jugador pueden compartir 
        caracteristicas y no deben tratarse automaticamente como observaciones
        independientes

    ->  La separacion entre entrenamiento y prueba se realiza por jugador, de esta
        forma se evita que un mismo UUID  aparezca en ambos conjuntos, reduciendo el 
        riesgo de obtener una evaluacion demasiado optimista por compartir jugadores

    -> Se utiliza MAE para representar el error absoluto promedio en minutos, RMSE
        para penalizar en mayor medida los errores grandes y R2 para desciribir
        la proporcion de variabilidad explicada por la recta en el conjunto evaluado
        .Ninguna de estas metricas debe de interpretarse de forma aislada

    ->  Las graficas de dispercion y residuos solo son apoyo para interpretar la 
        relacion y examinar posibles patrones en los errores. NO influyen
        directamente en las pruebas ni en las metricas numericas

------------------------------------------------>
INTERPRETACION DE LOS RESULTADOS VISTOS AL MOMENTO DE EJECICION
------------------------------------------------>
    Se pudo apreciar que existe una relacion negativa entre el ELO previo estimado y el
    tiempo de completacion, es decir, que los jugadores con mayor ELO tienden a completar las
    partidas en menos tiempo. Con la pendiente de la regresion podemos cuantificar que 
    aproximadamente por cada 100 puntos de ELO el tiempo de completacion de la partida se 
    reduce aproximadamente 1.15 minutos. 

    En este punto, el modelo logra estimaciones mas certeras que simplemente utilizar el tiempo
    promedio del conjunto de entrenamiento. Sin embargo, los errores de prediccion y los patrones
    de los residuos muestran que una regresion con una recta no es la mas adecuada, esto dado a que 
    no representa con exactitud los comportamientos de los datos, sobre todo en las de duracion extrema.

    Por lo que, el modelo resulta util para describir la tendencia en general de los datos y realizar
    aproximaciones, pero no para afirmar con seguridad el tiempo exacto que tardara un jugador con
    determinado ELO en completar una partida. 


------------------------------------------------>
LIMITACIONES DEL ANALISIS Y MODELO
------------------------------------------------>

    ->  La reconstruccion del ELO previo mediante elo- cambio_elo depende depende de la 
        interpretacion temporal de los campos de la fuente. La comparacion con jugador_elo
        presenta pocas coincidencias exacatas y no permite confirmar por si sola que los
        campos correspodan al mismo instante. Por ello, elo_previo_estimado debe 
        considerarse como una variable estimada y no una medicion historica
    
    ->  Una asociacion estadisticamente significativa no demuestra casualida. El tiempo
        de completacion puede depender de otros factores que no se incluyen en el modelo

    ->  La grafica de residuos muestra patrones sistematicos y una dispersion que aumenta
        para algunos tiempoes estimados, sugirienodo que la recta construida mediante regresion
        no captura todos los patrones presentes en los datos y que la variabilidad del error
        no es constante en todo el rango.

    ->  El modelo presenta dificultades con las partidas de extrema duracion; tiende a
        subestimar algunos tiempos muy largos y puede producir alguna prediccion cercana a cero
        o incluso negativa.

    ->  El MAE y el RMSE indican que las prediccion tienen errores relevantes incluso cuando
        mejoran frente al predictor constante de referencia. Por lo que, el modelo debe
        interpretarse como una aproximacion y no como un metodo para conocer con exactitud la 
        duracion de una partida individual-

    ->  Las metricas de entrenamiento y prueba corresponden a conjuntos diferentes y no deben
        de ser confundidos con el R2 descriptivo calculado sobre todos los datos para estudiar
        la relacion.
"""

from pathlib import Path
from contextlib import contextmanager
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import linregress, pearsonr, spearmanr
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import statsmodels.api as sm


"""
████████████████████████████████████████████████████████████████████████████
█  CONSTANTES Y RUTAS DE ARCHIVOS                                          █
████████████████████████████████████████████████████████████████████████████
"""
ALFA = 0.05
SEMILLA_ALEATORIA = 42
PROPORCION_PRUEBA = 0.20
MILISEGUNDOS_POR_MINUTO = 60_000
MINIMO_FILAS_MODELO = 20
CLAVE_RELACION = ["id_partida", "jugador_uuid"]

def resolver_base_dir():
    candidatos = [Path.cwd() / "MCSR_Ranked", Path.cwd(), Path(__file__).resolve().parent / "MCSR_Ranked", Path(__file__).resolve().parent]
    archivos_requeridos = [Path("data/final/main/partidas.csv"), Path("data/final/main/partida_jugadores.csv"), Path("data/final/aux/cambios_elo.csv"), Path("data/final/aux/completaciones.csv")]
    for candidato in candidatos:
        if all((candidato / archivo).is_file() for archivo in archivos_requeridos):
            return candidato.resolve()
    raise FileNotFoundError("No se localizo la carpeta del proyeco con los CSV requeridos. Ejecute el programa desde la raiz del repo o coloca el script junto a la carpeta MCSR_Ranked") 

BASE_DIR = resolver_base_dir()
FINAL_DIR = BASE_DIR / "data" / "final"
MAIN_DIR = FINAL_DIR / "main"
AUX_DIR = FINAL_DIR / "aux"
ACT5_DIR = BASE_DIR / "Act_5"
RESULTADOS_DIR = ACT5_DIR / "resultados"
RESULTADOS_DIR.mkdir(parents=True, exist_ok=True)
CSV_PARTIDA_JUGADORES = MAIN_DIR / "partida_jugadores.csv"
CSV_CAMBIOS_ELO = AUX_DIR / "cambios_elo.csv"
CSV_COMPLETACIONES = AUX_DIR / "completaciones.csv"
SALIDA_REPORTE = RESULTADOS_DIR / "reporte_act_5_modelo_lineal.txt"


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
█  CARGAR DATASET Y VALIDACION DE ESTRUCTURA                               █
████████████████████████████████████████████████████████████████████████████
"""
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

def normalizar_claves(tabla):
    tabla = tabla.copy()
    if "id_partida" in tabla.columns:
        tabla["id_partida"] = pd.to_numeric(tabla["id_partida"], errors="coerce").astype("Int64")
    if "jugador_uuid" in tabla.columns:
        tabla["jugador_uuid"] = tabla["jugador_uuid"].astype("string").str.strip().replace(r"^\s*$", pd.NA, regex=True)
    return tabla

def validar_claves_unicas(tabla, nombre, claves):
    columnas_inexistentes = [col for col in claves if col not in tabla.columns]
    if columnas_inexistentes:
        raise ValueError(f"La tabla {nombre} no contiene las columnas clave requeridas: {columnas_inexistentes}")
    mascara_nulos = tabla[claves].isna().any(axis=1)
    mascara_duplicados = tabla.duplicated(claves, keep=False)
    filas_sin_clave = int(mascara_nulos.sum())
    filas_duplicadas = int(mascara_duplicados.sum())
    print(f"{nombre:24} filas con clave incompleta: {filas_sin_clave:>8,}")
    print(f"{'':24} filas con clave duplicada: {filas_duplicadas:>8,}")
    if filas_sin_clave or filas_duplicadas:
        muestras = tabla.loc[mascara_nulos | mascara_duplicados, claves].head(10)
        raise ValueError(f"La tabla {nombre} no tiene una clave unica y completa ({claves}).\nIncompletos={filas_sin_clave}; duplicados={filas_duplicadas}.\nA revision:\n{muestras.to_string(index=False)}")

def cargar_tablas():
    imprimir_titulo("CARGANDO Y VALIDANDO TABLAS")
    tablas = {
        "partida_jugadores": cargar_dataset(CSV_PARTIDA_JUGADORES, "partida_jugadores", ["id_partida", "jugador_uuid", "jugador_elo"]),
        "cambios_elo": cargar_dataset(CSV_CAMBIOS_ELO, "cambios_elo", ["id_partida", "jugador_uuid", "cambio_elo", "elo"]),
        "completaciones": cargar_dataset(CSV_COMPLETACIONES, "completaciones", ["id_partida", "jugador_uuid", "tiempo_completacion_ms"])
    }
    for nombre, tabla in tablas.items():
        tablas[nombre] = normalizar_claves(tabla)
        validar_claves_unicas(tablas[nombre], nombre, CLAVE_RELACION)
    return tablas

def mostrar_calidad_datos(tablas):
    imprimir_titulo("CALIDAD DE LOS DATOS DE ENTRADA")
    analisis = {"partida_jugadores": ["jugador_elo"], "cambios_elo": ["cambio_elo", "elo"], "completaciones": ["tiempo_completacion_ms"]}
    indicadores = []
    for nombre, columnas_numericas in analisis.items():
        tabla = tablas[nombre]
        n_filas = len(tabla)
        for columna in columnas_numericas:
            valores_originales = tabla[columna]
            faltantes = valores_originales.isna()
            valores_numericos = pd.to_numeric(valores_originales, errors="coerce")
            indicadores.append({"Tabla": nombre, "Variable": columna, "Filas": n_filas, "Faltantes": int(faltantes.sum()), "No numericos": int((valores_numericos.isna() & ~faltantes).sum()), "No finitos": int(np.isinf(valores_numericos.to_numpy(dtype=float, na_value=np.nan)).sum())})
    tabla_calidad = pd.DataFrame(indicadores)
    imprimir_tabla(tabla_calidad)
    ruta_salida = RESULTADOS_DIR / "calidad_datos.csv"
    tabla_calidad.to_csv(ruta_salida, index=False, encoding="utf-8-sig")
    print(f"\nDiagnostico de calidad guardado en: {ruta_salida}")
        

def diagnosticar_campos_elo(tablas):
    imprimir_titulo("DIAGNOSTICO DE LOS CAMPOS DE ELO")
    df_jugadores = tablas["partida_jugadores"][CLAVE_RELACION + ["jugador_elo"]].copy()
    df_cambios = tablas["cambios_elo"][CLAVE_RELACION + ["elo", "cambio_elo"]].copy()
    df_jugadores["jugador_elo"] = pd.to_numeric(df_jugadores["jugador_elo"], errors="coerce")
    df_cambios["elo"] = pd.to_numeric(df_cambios["elo"], errors="coerce")
    df_cambios["cambio_elo"] = pd.to_numeric(df_cambios["cambio_elo"], errors="coerce")
    comparacion = df_jugadores.merge(df_cambios, on=CLAVE_RELACION, how="inner", validate="one_to_one")
    comparacion["elo_menos_cambio"] = comparacion["elo"] - comparacion["cambio_elo"]
    comparacion = comparacion.replace([np.inf, -np.inf], np.nan)
    mascara_elo = comparacion[["jugador_elo", "elo"]].notna().all(axis=1)
    mascara_cambio = comparacion[["jugador_elo", "elo", "cambio_elo", "elo_menos_cambio"]].notna().all(axis=1)
    if not mascara_elo.any() and not mascara_cambio.any():
        print("No hay filas suficientes para comparar los campos de ELO.")
        return
    comparacion["coincide_con_elo"] = pd.Series(pd.NA, index=comparacion.index, dtype="boolean")
    comparacion["coincide_con_elo_menos_cambio"] = pd.Series(pd.NA, index=comparacion.index, dtype="boolean")
    comparacion.loc[mascara_elo, "coincide_con_elo"] = comparacion.loc[mascara_elo, "jugador_elo"] == comparacion.loc[mascara_elo, "elo"]
    comparacion.loc[mascara_cambio, "coincide_con_elo_menos_cambio"] = comparacion.loc[mascara_cambio, "jugador_elo"] == comparacion.loc[mascara_cambio, "elo_menos_cambio"]
    coincidencias_elo = int(comparacion.loc[mascara_elo, "coincide_con_elo"].sum())
    coincidencias_cambio = int(comparacion.loc[mascara_cambio, "coincide_con_elo_menos_cambio"].sum())
    n_elo = int(mascara_elo.sum())
    n_cambio = int(mascara_cambio.sum())
    resumen = pd.DataFrame([
        {"Comparacion": "jugador_elo == elo", "Coincidencias": coincidencias_elo, "Filas comparables": n_elo, "Porcentaje": (100 * coincidencias_elo / n_elo if n_elo else np.nan)},
        {"Comparacion": "jugador_elo == elo - cambio_elo", "Coincidencias": coincidencias_cambio, "Filas comparables": n_cambio, "Porcentaje": (100 * coincidencias_cambio / n_cambio if n_cambio else np.nan),}
    ])
    resumen["Porcentaje"] = resumen["Porcentaje"].map(lambda valor: f"{valor:.2f}%" if pd.notna(valor) else "No disponible")
    imprimir_tabla(resumen)
    columnas_muestra = CLAVE_RELACION + ["jugador_elo", "elo", "cambio_elo", "elo_menos_cambio", "coincide_con_elo", "coincide_con_elo_menos_cambio",]
    mascara_comparable = mascara_elo | mascara_cambio
    muestra = comparacion.loc[mascara_comparable, columnas_muestra].head(12)
    print("\nMuestra de registros comparables:")
    imprimir_tabla(muestra)
    resumen.to_csv(RESULTADOS_DIR / "diagnostico_campos_elo.csv", index=False, encoding="utf-8-sig")
    print("\nNota: Las coincidencias comprueban igualdad numerica, no prueba por si solas si un rating corresponde al instante anterior o posterior de la partida")

def calcular_metricas(y_real, y_pred):
    return {"n_prueba": int(len(y_real)), "MAE": float(mean_absolute_error(y_real, y_pred)), "RMSE": float(np.sqrt(mean_squared_error(y_real, y_pred))), "R2": float(r2_score(y_real, y_pred)) if len(y_real) >= 2 else np.nan}

def imprimir_metricas(metricas, unidad):
    imprimir_tabla(pd.DataFrame([
        {"Metrica": "Observaciones en prueba", "Valor": f"{metricas['n_prueba']:,}"},
        {"Metrica": f"MAE ({unidad})", "Valor": f"{metricas['MAE']:.6f}"},
        {"Metrica": f"RMSE ({unidad})", "Valor": f"{metricas['RMSE']:.6f}"},
        {"Metrica": "R2", "Valor": f"{metricas['R2']:.6f}"}
    ]))

def formato_numero(valor, decimales=6):
    try:
        valor = float(valor)
        return "no disponible" if np.isnan(valor) else "infinito" if np.isinf(valor) else f"{valor:,.{decimales}f}"
    except(TypeError, ValueError):
        return str(valor)

def guardar_metricas(nombre, valores):
    pd.DataFrame([valores]).to_csv(RESULTADOS_DIR / nombre, index=False, encoding="utf-8-sig")

"""
████████████████████████████████████████████████████████████████████████████
█  MODELO                                                                  █
████████████████████████████████████████████████████████████████████████████
"""
def preparar_datos_modelo_1(tablas):
    imprimir_titulo("PREPARANDO DATOS PARA EL MODELO ")
    completaciones = tablas["completaciones"][CLAVE_RELACION + ["tiempo_completacion_ms"]].copy()
    cambios = tablas["cambios_elo"][CLAVE_RELACION + ["elo", "cambio_elo"]].copy()
    completaciones["tiempo_completacion_ms"] = pd.to_numeric(completaciones["tiempo_completacion_ms"], errors="coerce")
    cambios["elo"] = pd.to_numeric(cambios["elo"], errors="coerce")
    cambios["cambio_elo"] = pd.to_numeric(cambios["cambio_elo"], errors="coerce")
    unido = completaciones.merge(cambios, on=CLAVE_RELACION, how="left", validate="one_to_one", indicator=True)
    unido["elo_previo_estimado"] = unido["elo"] - unido["cambio_elo"]
    tiempo = unido["tiempo_completacion_ms"].to_numpy(dtype=float, na_value=np.nan)
    rating_previo = unido["elo_previo_estimado"].to_numpy(dtype=float, na_value=np.nan)
    emparejado = unido["_merge"].eq("both").to_numpy()
    tiempo_finito = np.isfinite(tiempo)
    elo_post_finito = np.isfinite(unido["elo"].to_numpy(dtype=float, na_value=np.nan))
    cambio_finito = np.isfinite(unido["cambio_elo"].to_numpy(dtype=float, na_value=np.nan))
    rating_finito = np.isfinite(rating_previo)
    valido = emparejado & tiempo_finito & (tiempo > 0) & elo_post_finito & cambio_finito & rating_finito & (rating_previo > 0)
    datos_validos = unido.loc[valido].drop(columns=["_merge"]).sort_values(CLAVE_RELACION).reset_index(drop=True)
    datos_validos["tiempo_completacion_minutos"] = datos_validos["tiempo_completacion_ms"] / MILISEGUNDOS_POR_MINUTO
    resumen_calidad = {
        "completaciones_originales": len(completaciones),
        "completaciones_sin_coincidencia_elo": int((~emparejado).sum()),
        "tiempos_faltantes_o_no_finitos": int((~tiempo_finito).sum()),
        "tiempos_no_positivos": int((tiempo_finito & (tiempo <= 0)).sum()),
        "elo_post_o_cambio_faltante_o_no_finito": int((emparejado & ~(elo_post_finito & cambio_finito)).sum()),
        "elo_previo_estimado_no_positivo": int((rating_finito & (rating_previo <= 0)).sum()), 
        "observaciones_validas": len(datos_validos),
        "jugadores_validos": int(datos_validos["jugador_uuid"].nunique()),
    }
    imprimir_titulo("RESUMEN DE PREPARACION DEL MODELO")
    imprimir_tabla(pd.DataFrame([{"Indicador": nombre.replace("_", " ").capitalize(), "Cantidad": valor} for nombre, valor in resumen_calidad.items()]))
    print("\nAdvertencia: `elo_previo_estimado = elo - cambio_elo` es una reconstruccion provisional del elo previo a la partida. Por lo que, no se debe describir como dato historico confirmado, esto ya que la API no cuenta con una documentacion adecuada y haciendo calculos anteriores no hubo concordancia. ")
    columnas_salida = CLAVE_RELACION + ["tiempo_completacion_ms", "tiempo_completacion_minutos", "elo", "cambio_elo", "elo_previo_estimado"]
    ruta_salida = RESULTADOS_DIR / "modelo_regresion_datos.csv"
    datos_validos[columnas_salida].to_csv(ruta_salida, index=False, encoding="utf-8-sig")
    print(f"Datos preparados guardados en {ruta_salida}")
    return datos_validos

def separar_por_jugador(datos):
    if not 0< PROPORCION_PRUEBA < 1: raise ValueError("No le muevas a PROPORCION_PRUEBA el valor debe ser entre 0 y 1. ¿Que haces? (._.) ඞ")
    jugadores = datos["jugador_uuid"].dropna().unique()
    if len(jugadores) < 5:
        raise ValueError("Hay al menos cinco jugadores con observaciones validas. Por lo que no se hara una particion por filas, debido a que se podria colocar al mismo jugador en ambos conjuntos.")
    generador = np.random.default_rng(SEMILLA_ALEATORIA)
    jugadores = generador.permutation(jugadores)
    cantidad_prueba = max(2, int(round(len(jugadores) * PROPORCION_PRUEBA)))
    cantidad_prueba = min(cantidad_prueba, len(jugadores) - 2)
    jugadores_prueba = set(jugadores[:cantidad_prueba])
    mascara_prueba = datos["jugador_uuid"].isin(jugadores_prueba)
    entrenamiento = datos.loc[~mascara_prueba].copy()
    prueba = datos.loc[mascara_prueba].copy()
    if len(entrenamiento) < 3 or len(prueba) < 2:
        raise ValueError("La separacion por jugador produjo conjutos demasiado pequeños.")
    return entrenamiento, prueba

def evaluar_modelo_1(datos, entrenamiento, prueba):
    x = datos["elo_previo_estimado"].to_numpy(dtype=float)
    y = datos["tiempo_completacion_ms"].to_numpy(dtype=float)
    if np.unique(x).size < 2 or np.unique(y).size < 2:
        raise ValueError("No se puede ajustar el modelo: el ELO o el tiempo no tienen variacion.")
    matriz_x = pd.DataFrame({"constante": np.ones(len(datos)), "elo_previo_estimado": x,}, index=datos.index)
    modelo = sm.OLS(y, matriz_x).fit(cov_type="cluster", cov_kwds={"groups": datos["jugador_uuid"], "use_correction": True}, use_t=True)
    intercepto = float(modelo.params["constante"])
    pendiente = float(modelo.params["elo_previo_estimado"])
    p_valor = float(modelo.pvalues["elo_previo_estimado"])
    intervalo = modelo.conf_int(alpha=ALFA).loc["elo_previo_estimado"]
    ic_inferior = float(intervalo.iloc[0])
    ic_superior = float(intervalo.iloc[1])
    correlacion_pearson = pearsonr(x, y)
    correlacion_spearman = spearmanr(x, y)
    x_entrenamiento = entrenamiento["elo_previo_estimado"].to_numpy(dtype=float)
    y_entrenamiento = entrenamiento["tiempo_completacion_ms"].to_numpy(dtype=float)
    if np.unique(x_entrenamiento).size < 2 or np.unique(y_entrenamiento).size < 2:
        raise ValueError("El elo de entrenamiento no tiene variaciones suficientes para ajustar una recta")
    modelo_entrenamiento = linregress(x_entrenamiento, y_entrenamiento)
    x_prueba = prueba["elo_previo_estimado"].to_numpy(dtype=float)
    y_prueba = prueba["tiempo_completacion_ms"].to_numpy(dtype=float)
    y_estimado = modelo_entrenamiento.intercept + modelo_entrenamiento.slope * x_prueba
    metricas_prueba = calcular_metricas(y_prueba, y_estimado)
    metricas = {
        "modelo": "ELO previo estimado frente al tiempo de completacion",
        "n_total": len(datos),
        "n_jugadores": int(datos["jugador_uuid"].nunique()),
        "pearson_r": float(correlacion_pearson.statistic),
        "pearson_p": float(correlacion_pearson.pvalue),
        "spearman_rho": float(correlacion_spearman.statistic),
        "spearman_p": float(correlacion_spearman.pvalue),
        "pendiente_minutos_por_punto_elo": pendiente / MILISEGUNDOS_POR_MINUTO,
        "pendiente_minutos_por_100_elo": pendiente * 100 / MILISEGUNDOS_POR_MINUTO,
        "intercepto_minutos": intercepto / MILISEGUNDOS_POR_MINUTO,
        "r2_ajuste_completo": float(modelo.rsquared),
        "pendiente_ic95_inferior": ic_inferior / MILISEGUNDOS_POR_MINUTO,
        "pendiente_ic95_superior": ic_superior / MILISEGUNDOS_POR_MINUTO,
        "p_pendiente_regresion": p_valor,
        "n_observaciones_entrenamiento": len(entrenamiento),
        "n_jugadores_entrenamiento": int(entrenamiento["jugador_uuid"].nunique()),
        "n_observaciones_prueba": len(prueba),
        "n_jugadores_prueba": int(prueba["jugador_uuid"].nunique()),
        "mae_prueba_minutos": metricas_prueba["MAE"] / MILISEGUNDOS_POR_MINUTO,
        "rmse_prueba_minutos": metricas_prueba["RMSE"] / MILISEGUNDOS_POR_MINUTO,
        "r2_prueba": metricas_prueba["R2"],
        "pendiente_entrenamiento_minutos_por_punto_elo": float(modelo_entrenamiento.slope) / MILISEGUNDOS_POR_MINUTO,
        "intercepto_entrenamiento_minutos": float(modelo_entrenamiento.intercept) / MILISEGUNDOS_POR_MINUTO
    }
    predicciones = prueba[CLAVE_RELACION + ["elo_previo_estimado", "tiempo_completacion_ms"]].copy()
    predicciones["tiempo_completacion_minutos"] = y_prueba / MILISEGUNDOS_POR_MINUTO
    predicciones["tiempo_estimado_ms"] = y_estimado
    predicciones["tiempo_estimado_minutos"] = y_estimado / MILISEGUNDOS_POR_MINUTO
    predicciones["residuo_ms"] = y_prueba - y_estimado
    predicciones["residuo_minutos"] = predicciones["residuo_ms"] / MILISEGUNDOS_POR_MINUTO    
    predicciones.to_csv(RESULTADOS_DIR / "predicciones_modelo_1.csv", index=False, encoding="utf-8-sig")
    return metricas, modelo_entrenamiento, predicciones

def guardar_graficas_modelo_1(entrenamiento, datos, modelo_entrenamiento, predicciones):
    plt.style.use("seaborn-v0_8-whitegrid")
    figura, eje = plt.subplots(figsize=(10, 6))
    eje.scatter(datos["elo_previo_estimado"], datos["tiempo_completacion_ms"] / MILISEGUNDOS_POR_MINUTO, alpha=0.22, s=17, edgecolors="none", label="Completaciones observadas")
    valores_x = np.linspace(float(entrenamiento["elo_previo_estimado"].min()), float(entrenamiento["elo_previo_estimado"].max()), 250)
    eje.plot(valores_x, (modelo_entrenamiento.intercept + modelo_entrenamiento.slope * valores_x) / MILISEGUNDOS_POR_MINUTO, linewidth=2.2, label="Recta ajustada con entrenamiento")
    eje.set_title("ELO previo estimado frente al tiempo de completacion")
    eje.set_xlabel("ELO previo estimado")
    eje.set_ylabel("Tiempo de completacion (minutos)")
    eje.legend()
    figura.tight_layout()
    figura.savefig(RESULTADOS_DIR / "dispersion_elo_tiempo.png", dpi=160, bbox_inches="tight")
    plt.close(figura)

    figura, eje = plt.subplots(figsize=(10, 6))
    eje.scatter(predicciones["tiempo_estimado_minutos"], predicciones["residuo_minutos"], alpha=0.35, s=18, edgecolors="none")
    eje.axhline(0, linewidth=1.5, linestyle="--")
    eje.set_title("Residuos del Modelo 1 en el conjunto de prueba")
    eje.set_xlabel("Tiempo estimado (minutos)")
    eje.set_ylabel("Residuo: observado - estimado (minutos)")
    figura.tight_layout()
    figura.savefig(RESULTADOS_DIR / "residuos_modelo_1.png", dpi=160, bbox_inches="tight")
    plt.close(figura)

def ejecutar_modelo_1(tablas):
    imprimir_titulo("MODELO - ELO PREVIO ESTIMADO Y TIEMPO DE COMPLETACION")
    datos = preparar_datos_modelo_1(tablas)
    if len(datos) < MINIMO_FILAS_MODELO:
        raise ValueError(f"Solo hay {len(datos)} observaciones validas. Al menos se requieren {MINIMO_FILAS_MODELO} para ajustar el modelo")
    entrenamiento, prueba = separar_por_jugador(datos)
    metricas, modelo_entrenamiento, predicciones = evaluar_modelo_1(datos, entrenamiento, prueba)
    imprimir_titulo("CORRELACION Y REGRESION - MODELO ")
    imprimir_tabla(pd.DataFrame([
        {"Indicador": "Pearson r", "Valor": formato_numero(metricas["pearson_r"])},
        {"Indicador": "Pearson p", "Valor": formato_numero(metricas["pearson_p"], 10)},
        {"Indicador": "Spearman rho", "Valor": formato_numero(metricas["spearman_rho"])},
        {"Indicador": "Spearman p", "Valor": formato_numero(metricas["spearman_p"], 10)},
        {"Indicador": "Pendiente por punto de ELO (minutos)", "Valor": formato_numero(metricas["pendiente_minutos_por_punto_elo"], 10)},
        {"Indicador": "Pendiente por 100 puntos de ELO (minutos)", "Valor": formato_numero(metricas["pendiente_minutos_por_100_elo"])},
        {"Indicador": "Intercepto (minutos)", "Valor": formato_numero(metricas["intercepto_minutos"])},
        {"Indicador": "R2 descriptivo (datos completos)", "Valor": formato_numero(metricas["r2_ajuste_completo"])},
        {"Indicador": "IC 95% inferior de la pendiente", "Valor": formato_numero(metricas["pendiente_ic95_inferior"], 10)},
        {"Indicador": "IC 95% superior de la pendiente", "Valor": formato_numero(metricas["pendiente_ic95_superior"], 10)},
        {"Indicador": "p de la pendiente", "Valor": formato_numero(metricas["p_pendiente_regresion"], 10)}
    ]))
    p_valor = metricas["p_pendiente_regresion"]
    se_rechaza_H0 = p_valor < ALFA
    print(f"{"-"*50}\n DECISION SOBRE HIPOTESIS NULA\n{"-"*50}")
    print(f"Nivel de significancia (alpha): {ALFA}\nValor de p obtenido: {p_valor:.4e}\n")
    print("CONCLUSION:")
    print("\tSe RECHAZA la hipotesis nula. Por lo que, existe evidencia estadisticamente significativa\n\tde que el ELO previo estimado influye linealmente en el tiempo de completacion." if se_rechaza_H0 else "NO SE RECHAZA la hipotesis nula. Por lo que, no se cuenta con evidencia estadisticamente\n\t suficiente para afirmar que existe una realcion lineal significativa.") 
    imprimir_titulo("EVALUACION PREDICTIVA DEL MODELO 1")
    print(f"Entrenamiento: {metricas['n_observaciones_entrenamiento']:,} observaciones de {metricas['n_jugadores_entrenamiento']:,} jugadores")
    print(f"Prueba: {metricas['n_observaciones_prueba']:,} observaciones de {metricas['n_jugadores_prueba']:,} jugadores")
    imprimir_metricas({"n_prueba": metricas["n_observaciones_prueba"], "MAE": metricas["mae_prueba_minutos"], "RMSE": metricas["rmse_prueba_minutos"], "R2": metricas["r2_prueba"],}, "minutos")
    print("NOTAS:\n\t-> La evaluacion predictiva se realizo con jugadores no utilizados durante el entrenamiento.\n\t-> Los valores p de Pearson y Spearman usan metodos concencionales que no corrigen la dependencia de observaciones repetidas de un jugador.\n\t-> El elo previo se construye como elo - cambio_elo; dada la falta de documentacion de la API.")
    guardar_metricas("metricas_modelo_1.csv", metricas)
    guardar_graficas_modelo_1(entrenamiento, datos, modelo_entrenamiento, predicciones)
    print("Graficas guardadas: dispersion_elo_tiempo.png y residuos_modelo_1.png")
    print("Predicciones guardadas: predicciones_modelo_1.csv")

"""
████████████████████████████████████████████████████████████████████████████
█  EJECUCION DE LA ACTIVIDAD 5                                             █
████████████████████████████████████████████████████████████████████████████
"""

def ejecutar_act5():
    with registrar_salida(SALIDA_REPORTE):
        imprimir_titulo("ACTIVIDAD 5 - MODELO LINEAL Y CORRELACION")
        print(f"Directorio Base:\t{BASE_DIR}")
        print(f"Directorio de resultados:\t{RESULTADOS_DIR}")
        print(f"Proporcion de prueba:\t{PROPORCION_PRUEBA:.0%}")
        print(f"Semilla aleatorio:\t{SEMILLA_ALEATORIA}")
        print(f"Nivel de significancia:\t{ALFA}")
        try:
            tablas = cargar_tablas()
            mostrar_calidad_datos(tablas)
            diagnosticar_campos_elo(tablas)
        except Exception as error:
            imprimir_titulo("ERROR EN LA PREPARACION DE LOS DATOS")
            print(f"Tipo de error: {type(error).__name__}")
            print(f"Descripcion: {error}")
            print("\nNo se ejecutara el programa hasta corregir los problemas de entrada.")
            print(f"\nReporte generado: {SALIDA_REPORTE}")
            return
        try:
            ejecutar_modelo_1(tablas)
        except Exception as error:
            imprimir_titulo("ERROR AL MOMENTO DE CONSTRUIR EL MODELO")
            print(f"Tipo de error: {type(error).__name__}")
            print(f"Descripcion: {error}")
            print("\nLa construccion del modelo no pudo finalizar correctamente. Favor de revisa el error y los resultados generados antes de la interrupcion.")
            print(f"\nReporte de ejecucion: {SALIDA_REPORTE}")
            print(f"Directorio de resultados: {RESULTADOS_DIR}")
            return
        imprimir_titulo("EJECUCION COMPLETADA")
        print(f"Reporte completo: {SALIDA_REPORTE}")
        print(f"Directorio de resultados: {RESULTADOS_DIR}")

if __name__ == "__main__":
    ejecutar_act5()