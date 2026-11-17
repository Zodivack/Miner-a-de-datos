"""
████████████████████████████████████████████████████████████████████████████
█  ACTIVIDAD 8 - PRONOSTICO DE ACTIVIDAD Y COMPOSICION DE PARTIDAS         █
████████████████████████████████████████████████████████████████████████████

-------------------------------------------------------------------------->
DESCRIPCION GENERAL DEL PROGRAMA
-------------------------------------------------------------------------->

    Esta practica consisten en analizar la composicion textual de los
    nombres de los jugaores registrados en el dataset de MCSR Ranked
    (temporada 10), mediante la utilizacion de tecnicas de procesamiento
    y analisis exploratorio de texto. Para su elaboracion se utilizo la
    tabla de jugadores.csv, especificamente la variable de su nombre
    (jugador_nombre).

    Con la realizacion de esta practica se tiene como objetivo identificar
    patron en la escritura de los nombres de los usarios, estudiar la
    frecuencia de los fragmentos alfabeticos y sus combinaciones, asi como
    describir sus caracteristicas de formato y longitud de estos. Todo se
    consiguira, normalizando los nombres y dividiendolos en fragmentos
    alfabeticos y numericos, para posteriormente calcular las frecuencias,
    biagrams y estadisticas descriptivas, generando con ello una nube
    de palabras y algunas graficas para facilitar la comprension de los 
    resultados obtenidos.

    La salida esperada del programa son archivos CSV, con resultados del
    procesamiento y analisis, graficas en formato png y un reporte TXT
    que reune los resultados obtenidos durante la ejecucion.

-------------------------------------------------------------------------->
PROCEDIMIENTO
-------------------------------------------------------------------------->
    Unidad de analisis:
        ->  Cada observacion representa un nombre de usuario registrado
            en el dataset correspondiente a la variable textual de la 
            columna jugador_nombre
        ->  Se utiliza el uuid del jugador para revisar su integridad

    Procesamiento del nombre:
        ->  Se normaliza de forma unicode mediante NKFC y se eliminan 
            espacios presentes en el nombre
        ->  Procede a convertirse a minisculas para su comprobacion y
            analisis de frecuencias
        ->  Se separa en fragmentos mediante cambios de mayuscula,
            separadores y transiciones entre letras y numeros
        ->  Realiza una identificacion independiente de fragmentos
            alfabeticos y numericos
        ->  Se excluyen los fragmentos alfabeticos con menos de dos 
            caracteres
    
    Se analiza:
        ->  La frecuencia de fragmentos. Contabilizando las apariciones de 
            cada fragmneto alfabetico y la cantidad de nombres en los que 
            aparecen
        ->  Los Biagramas. Identificando las combinaciones de dos fragmentos
            alfabeticos consecutivos dentro de un mismo nombre
        ->  La longitud. Midiendo la cantidad de caracteres utilizados en
            los nombres
        ->  Los patrones de formatos. Identificando caracterisiticas, como
            mayusculas, numeros, guione bajo, guiones, espacios y la 
            presencia de varios fragmentos alfabeticos
        ->  La nube de palabras. Representando visualmente los fragmentos
            alfabeticos segun su frecuencia

-------------------------------------------------------------------------->
JUSTIFICACION DE DECISIONES TOMADAS
-------------------------------------------------------------------------->    
    ->  Se conserva el identificador jugador_uuid, para comprobar que los 
        registros tengan claves completas y unicas, asi evitando analizar 
        informacion asociada a registros inconsistentes

    ->  Se aplica normalizacion Unicode, eliminacion de espacios innecesarios 
        y conversion a minusculas, para facilitar la comparación de nombres 
        y el conteo de frecuencias sin depender de diferencias de escritura 
        que no modifican el contenido esencial

    ->  Se utiliza una tokenizacion basada en cambios de mayusculas, 
        separadores y transiciones entre letras y numeros, para identificar 
        fragmentos reconocibles sin dividir arbitrariamente nombres que 
        tienen palabras concatenadas en minusculas

    ->  Para evitar la aparición de elementos muy pequeños dentro de los 
        fragmentos alfabeticos se ha establecido un minimo de 2 caracteres
        , para evitar elementos que aporten poco o nada al analisis
    
    ->  No se han usado tecnicas como la eliminacion de palabras vacias, 
        lematizacion o sentimientos, ya que los nombres de usuario no son 
        un conjunto del lenguaje natural. Por lo que, el uso de estas 
        tecnicas podria provocar la eliminacion o modificacion de los 
        fragmentos que componen los nombres de los jugadores

    ->  Se analizan tanto la frecuencia total de cada fragmento como la 
        cantidad de nombres que lo incluyen, dado que ambas medidas permiten 
        distinguir entre la frecuencia de uso y su distribucion entre los 
        jugadores

    ->  Se añaden bigramas, para identificar combinaciones consecutivas de 
        fragmentos, mientras que las estadisticas de longitud y formato 
        permiten estudiar características que no pueden apreciarse 
        unicamente mediante la nube de palabras
    
-------------------------------------------------------------------------->
INTERPRETACION DE RESULTADOS
-------------------------------------------------------------------------->

    Se encontro que en los nombres de usuario estan compuestos por una gran
    diversidad de elementos, con poca repeticion de fragmentos y pocas
    combinaciones entre ellos. Esto nos dice que la mayoria de jugadores
    tienden a usar nicknames muy particulares o muy unicos para ellos, en
    lugar de solo apegarse a un vocabulario y conjunto de expresiones.

    Dentro de los nombres, se observa que se utiliza mezclas de diferentes
    tipos de escritura; mayusculas, numeros e inculuso varios fragmentos de
    otro vocabularios. Sin embargo, realmente estos aspectos hablan mas de
    los gustos de las personas por el formato y composcion de sus nombres, 
    que no necesariamente tienen que tener un significado. 

    Los resultados de esta practica apunta a que los nombres de los 
    jugadores representan para ellos mas un identificador unico universal,
    que una composicion linguistica que tenga algun significado. Por lo que,
    se consiguio analizar patrones de escritura y estructura que suelen emplear
    algunas personas cuando intentan ser originales, pero no opiniones ni 
    sentimientos o caracteristicas personales unicas de las personas.
"""

from pathlib import Path
from contextlib import contextmanager
import numpy as np
import pandas as pd
import sys
import re
import unicodedata
from collections import Counter
from itertools import pairwise
from wordcloud import WordCloud
import matplotlib.pyplot as plt

"""
████████████████████████████████████████████████████████████████████████████
█  CONSTANTES Y RUTAS DE ARCHIVOS                                          █
████████████████████████████████████████████████████████████████████████████
"""
SEMILLA_ALEATORIA = 42
MINIMO_LONGITUD_TOKEN = 2
TOP_TERMINOS_GRAFICA = 20
MAX_TERMINOS_NUBE = 100
ARCHIVO_JUGADORES = Path("data/final/main/jugadores.csv")
CARPETA_RESULTADOS = Path("Act_9/resultados")
CARPETA_CSV = CARPETA_RESULTADOS / "csv"
CARPETA_GRAFICAS = CARPETA_RESULTADOS / "graficas"
COLUMNAS_JUGADORES = ["jugador_uuid", "jugador_nombre"]
ARCHIVOS_CSV = {"resumen_calidad_.csv": "calidad", "estadisticas_texto.csv": "estadisticas", "nombres_usuario_procesados.csv": "nombres_procesados", "frecuencias_tokens.csv": "frecuencias_tokens", "frecuencias_bigramas.csv": "frecuencias_bigramas", "patrones_formato.csv": "patrones_formato", 
    "distribucion_longitud.csv": "distribucion_longitud"}
ARCHIVOS_GRAFICAS = ["nube_palabras_nombres_usuario.png", "frecuencia_tokens.png", "distribucion_longitud_nombres.png", "patrones_formato_nombres.png", "frecuencia_bigramas.png"]

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
    archivos = [ARCHIVO_JUGADORES]
    for candidato in candidatos:
        if all((candidato / archivo).is_file() for archivo in archivos):
            return candidato.resolve()
        if all((candidato / "MCSR_Ranked" / archivo).is_file() for archivo in archivos):
            return (candidato / "MCSR_Ranked").resolve()        
    raise FileNotFoundError("No se localizo la carpeta raiz de MCSR_Ranked ni los archivos CSV requeridos. Verifique la ubicacion del proyecto.")

def normalizar_id(serie): return pd.to_numeric(serie, errors="coerce").astype("Int64")

def normalizar_nombre(valor):
    if pd.isna(valor):
        return pd.NA
    texto = re.sub(r"\s+", " ", unicodedata.normalize("NFKC", str(valor)).strip())
    return texto.casefold() if texto else pd.NA

"""
████████████████████████████████████████████████████████████████████████████
█  CARGA, VALIDACION Y NORMALIZACION DE LOS DATOS                          █
████████████████████████████████████████████████████████████████████████████
"""
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
    imprimir_titulo("ARCHIVOS DE ENTRADA")
    jugadores = cargar_dataset(base_dir / ARCHIVO_JUGADORES, "jugadores", COLUMNAS_JUGADORES)
    jugadores["jugador_uuid"] = normalizar_id(jugadores["jugador_uuid"])
    jugadores["jugador_nombre"] = jugadores["jugador_nombre"].astype("string")
    imprimir_titulo("VALIDACION DE CLAVES")
    calidad_claves = validar_claves_unicas(jugadores, "jugadores", ["jugador_uuid"])
    return jugadores, calidad_claves

"""
████████████████████████████████████████████████████████████████████████████
█  PROCESAMIENTO Y TOKENIZACION                                            █
████████████████████████████████████████████████████████████████████████████
"""
def extraer_fragmentos(nombre):
    if pd.isna(nombre):
        return [], [], [], 0
    
    def limpiar_y_dividir(t):
        texto_normalizado = unicodedata.normalize("NFKC", str(t)).strip()
        texto_CamelCase = re.sub(r"(?<=[a-záéíóúüñ])(?=[A-ZÁÉÍÓÚÜÑ])|(?<=[A-ZÁÉÍÓÚÜÑ])(?=[A-ZÁÉÍÓÚÜÑ][a-záéíóúüñ])", " ", texto_normalizado)
        return re.sub(r"(?<=[^\W\d_])(?=\d)|(?<=\d)(?=[^\W\d_])", " ", texto_CamelCase, flags=re.UNICODE)
    
    texto = limpiar_y_dividir(nombre)
    fragmentos = re.findall(r"[^\W\d_]+|\d+", texto, flags=re.UNICODE)
    tokens_numericos = [fragmento for fragmento in fragmentos if fragmento.isdigit()]
    tokens_alfabeticos = [fragmento.casefold() for fragmento in fragmentos if fragmento.isalpha() and len(fragmento.casefold()) >= MINIMO_LONGITUD_TOKEN]
    tokens_cortos = sum(1 for fragmento in fragmentos if fragmento.isalpha() and len(fragmento.casefold()) < MINIMO_LONGITUD_TOKEN)
    return fragmentos, tokens_alfabeticos, tokens_numericos, tokens_cortos

def crear_registro_procesado(fila):
    original = unicodedata.normalize("NFKC", str(fila["jugador_nombre"])).strip()
    fragmentos, tokens, numeros, tokens_cortos = extraer_fragmentos(original)
    cantidad_digitos = sum(c.isdigit() for c in original)
    cantidad_simbolos = sum(not c.isalnum() and not c.isspace() for c in original)
    return {
        "jugador_uuid": fila["jugador_uuid"], "jugador_nombre": original, "nombre_normalizado": normalizar_nombre(original), "fragmentos_detectados": " | ".join(fragmentos), "tokens_alfabeticos": " | ".join(tokens), "tokens_numericos": " | ".join(numeros), "longitud_nombre": len(original),
        "cantidad_letras": sum(caracter.isalpha() for caracter in original), "cantidad_digitos": cantidad_digitos, "cantidad_simbolos": cantidad_simbolos, "cantidad_tokens_alfabeticos": len(tokens), "tokens_cortos_excluidos": tokens_cortos, "contiene_mayusculas": any(c.isupper() for c in original),
        "contiene_numeros": cantidad_digitos > 0, "contiene_guion_bajo": "_" in original, "contiene_guion": any(c in original for c in "-‐‑‒–—"), "contiene_espacios": any(c.isspace() for c in original), "contiene_simbolos": cantidad_simbolos > 0, "contiene_varios_tokens": len(tokens) > 1,
        "_secuencia_bigramas": [fragmento.casefold() if fragmento.isalpha() and len(fragmento) >= MINIMO_LONGITUD_TOKEN else None for fragmento in fragmentos]
    }

def preparar_nombres(jugadores):
    datos = jugadores.copy()
    datos["nombre_normalizado"] = datos["jugador_nombre"].map(normalizar_nombre)
    mascara_valida = datos["nombre_normalizado"].notna()
    nombres_validos = datos.loc[mascara_valida].copy()
    if nombres_validos.empty:
        raise ValueError("No se encontraron nombres de usuario validos para analizar.")
    procesados = pd.DataFrame([crear_registro_procesado(fila) for _, fila in nombres_validos.iterrows()])
    frecuencias_nombres = procesados["nombre_normalizado"].value_counts()
    procesados["nombre_repetido_normalizado"] = procesados["nombre_normalizado"].map(frecuencias_nombres).gt(1)
    tokens_por_nombre = [[t for t in str(v).split(" | ") if t] for v in procesados["tokens_alfabeticos"]]
    secuencias_bigramas = procesados["_secuencia_bigramas"].tolist()
    procesados = procesados.drop(columns="_secuencia_bigramas")
    return procesados, mascara_valida, tokens_por_nombre, secuencias_bigramas

"""
████████████████████████████████████████████████████████████████████████████
█  ANALISIS DE EXPLORACION Y DE FRECUENCIAS                                █
████████████████████████████████████████████████████████████████████████████
"""
def crear_resumen_calidad(jugadores, calidad_claves, procesados, mascara_valida):
    nombres_vacios = int((~mascara_valida).sum())
    filas = [
        ("Registros originales en jugadores.csv", len(jugadores)), ("UUID faltantes", calidad_claves["incompletas"]), ("UUID duplicados", calidad_claves["duplicadas"]), ("Nombres faltantes o vacios", nombres_vacios), ("Nombres disponibles para analisis", len(procesados)),
        ("Nombres unicos normalizados", int(procesados["nombre_normalizado"].nunique())), ("Registros cuyo nombre esta repetido", int(procesados["nombre_repetido_normalizado"].sum())),("Nombres sin fragmentos alfabeticos validos", int(procesados["cantidad_tokens_alfabeticos"].eq(0).sum()))
    ]
    return pd.DataFrame(filas, columns=["Indicador", "Cantidad"])

def crear_estadisticas_texto(procesados):
    longitudes = procesados["longitud_nombre"].astype(float)
    fila = {
        "Nombres_analizados": len(procesados), "Nombres_unicos_normalizados": int(procesados["nombre_normalizado"].nunique()), "Tokens_alfabeticos_totales": int(procesados["cantidad_tokens_alfabeticos"].sum()),
        "Tokens_alfabeticos_unicos": len({token for valor in procesados["tokens_alfabeticos"] for token in str(valor).split(" | ") if token}), "Longitud_media": float(longitudes.mean()), "Longitud_mediana": float(longitudes.median()),
        "Longitud_desviacion_estandar": float(longitudes.std(ddof=1)) if len(longitudes) > 1 else 0.0, "Longitud_minima": int(longitudes.min()), "Longitud_Q1": float(longitudes.quantile(0.25)), "Longitud_Q3": float(longitudes.quantile(0.75)), "Longitud_maxima": int(longitudes.max()),
        "Promedio_tokens_alfabeticos_por_nombre": float(procesados["cantidad_tokens_alfabeticos"].mean()), "Nombres_con_numeros_pct": float(100 * procesados["contiene_numeros"].mean()),"Nombres_con_varios_tokens_pct": float(100 * procesados["contiene_varios_tokens"].mean()),
    }
    return pd.DataFrame([fila])

def crear_frecuencias(tokens_por_nombre, secuencias_bigramas, cantidad_nombres):
    contador = Counter(token for tokens in tokens_por_nombre for token in tokens)
    documentos = Counter(token for tokens in tokens_por_nombre for token in set(tokens))
    pares_bigramas = (f"{primero} {segundo}" for secuencia in secuencias_bigramas for primero, segundo in pairwise(secuencia) if primero is not None and segundo is not None)
    contador_bigramas = Counter(pares_bigramas)
    documentos_bigramas = Counter(bigrama for secuencia in secuencias_bigramas for bigrama in set(f"{primero} {segundo}" for primero, segundo in pairwise(secuencia) if primero is not None and segundo is not None))
    crear_fila_token = lambda token, freq: {"Token": token, "Frecuencia": freq, "Nombres_con_token": documentos[token], "Porcentaje_nombres": 100 * documentos[token] / cantidad_nombres, "Porcentaje_apariciones": 100 * freq /  max(sum(contador.values()), 1)}
    crear_fila_bigrama = lambda bigrama, freq: {"Bigram": bigrama, "Frecuencia": freq, "Nombres_con_bigrama": documentos_bigramas[bigrama], "Porcentaje_nombres": 100 * documentos_bigramas[bigrama] / cantidad_nombres}
    filas_tokens = [crear_fila_token(token, frecuencia) for token, frecuencia in contador.most_common()]
    filas_bigramas = [crear_fila_bigrama(bigrama, frecuencia) for bigrama, frecuencia in contador_bigramas.most_common()]
    return pd.DataFrame(filas_tokens), pd.DataFrame(filas_bigramas), contador

def crear_patrones_formato(procesados):
    configuraciones = [("Mayusculas", "contiene_mayusculas"), ("Numeros", "contiene_numeros"), ("Guion bajo (_)", "contiene_guion_bajo"), ("Guion (-)", "contiene_guion"), ("Espacios", "contiene_espacios"), ("Otros simbolos", "contiene_simbolos"),
        ("Varios fragmentos alfabeticos", "contiene_varios_tokens")]
    evaluar_patron = lambda nom_cat, col: {"Caracteristica": nom_cat, "Cantidad_nombres": (cant := int(procesados[col].sum())), "Porcentaje_nombres": 100 * cant / len(procesados)}
    return pd.DataFrame([evaluar_patron(nombre, col) for nombre, col in configuraciones])

def crear_distribucion_longitud(procesados):
    etiquetas = ["1-5", "6-10", "11-15", "16-20", "21-25", "26-30", "31 o mas"]
    grupos = pd.cut(procesados["longitud_nombre"], bins=[0, 5, 10, 15, 20, 25, 30, np.inf], labels=etiquetas, include_lowest=True, right=True)
    conteos = grupos.value_counts(sort=False).reindex(etiquetas, fill_value=0)
    tabla = conteos.rename_axis("Rango_caracteres").reset_index(name="Cantidad_nombres")
    tabla["Porcentaje_nombres"] = 100 * tabla["Cantidad_nombres"] / len(procesados)
    return tabla

"""
████████████████████████████████████████████████████████████████████████████
█  VISUALIZACION                                                           █
████████████████████████████████████████████████████████████████████████████
"""
def _crear_figura_vacia(mensaje, ruta):
    figura, eje = plt.subplots(figsize=(11, 6))
    eje.text(0.5, 0.5, mensaje, ha="center", va="center")
    eje.axis("off")
    figura.savefig(ruta, dpi=180, bbox_inches="tight")
    plt.close(figura)


def _generar_grafica_barras(datos, x_col, y_col, ruta, titulo, xlabel, ylabel, xlim=None, con_etiquetas=False):
    if datos.empty:
        _crear_figura_vacia("No hay datos", ruta)
        return
    figura, eje = plt.subplots(figsize=(11, 6))
    eje.barh(datos[x_col], datos[y_col])
    eje.set(xlabel=xlabel, ylabel=ylabel, title=titulo)
    if xlim:
        eje.set_xlim(xlim)
    eje.grid(axis="x", alpha=0.25)
    if con_etiquetas:
        for indice, valor in enumerate(datos[y_col]):
            eje.text(valor + 0.8, indice, f"{valor:.1f}%", va="center", fontsize=9)
    figura.tight_layout()
    figura.savefig(ruta, dpi=180, bbox_inches="tight")
    plt.close(figura)


def guardar_nube_palabras(frecuencias, ruta):
    if WordCloud is None:
        raise ImportError("No esta instalada la wordcloud. Instalala...")
    if not frecuencias:
        _crear_figura_vacia("No se identificaron fragmentos alfabeticos suficientes", ruta)
        return
    nube = WordCloud(width=1800, height=1000, background_color="white", colormap="viridis", max_words=MAX_TERMINOS_NUBE, min_font_size=8, collocations=False, prefer_horizontal=0.90, random_state=SEMILLA_ALEATORIA).generate_from_frequencies(dict(frecuencias))
    figura, eje = plt.subplots(figsize=(13, 7))
    eje.imshow(nube, interpolation="bilinear")
    eje.set_title("Fragmentos alfabeticos detectados en nombres de usuario", fontsize=15, pad=14)
    eje.axis("off")
    figura.tight_layout()
    figura.savefig(ruta, dpi=180, bbox_inches="tight")
    plt.close(figura)


def guardar_grafica_longitudes(procesados, ruta):
    figura, eje = plt.subplots(figsize=(10, 6))
    eje.hist(procesados["longitud_nombre"], bins=range(1, int(procesados["longitud_nombre"].max()) + 2), edgecolor="black", alpha=0.85)
    eje.set(title="Distribucion de la longitud de nombres de usuario", xlabel="Cantidad de caracteres", ylabel="Cantidad de nombres")
    eje.grid(axis="y", alpha=0.25)
    figura.tight_layout()
    figura.savefig(ruta, dpi=180, bbox_inches="tight")
    plt.close(figura)

def guardar_graficas(procesados, frecuencias, bigramas, patrones, graficas_dir):
    config_barras = {
        ARCHIVOS_GRAFICAS[1]: {"datos": frecuencias.head(TOP_TERMINOS_GRAFICA).sort_values("Frecuencia"), "x": "Token", "y": "Frecuencia", "titulo": f"{min(TOP_TERMINOS_GRAFICA, len(frecuencias))} fragmentos mas frecuentes", "xlabel": "Cantidad de apariciones", "ylabel": "Fragmento alfabetico"},
        ARCHIVOS_GRAFICAS[3]: {"datos": patrones.sort_values("Porcentaje_nombres"), "x": "Caracteristica", "y": "Porcentaje_nombres", "titulo": "Caracteristicas de formato presentes en los nombres", "xlabel": "Nombres que presentan la caracteristica (%)", "ylabel": "Caracteristica", "xlim": (0, 100), 
            "con_etiquetas": True},
        ARCHIVOS_GRAFICAS[4]: {"datos": bigramas.head(TOP_TERMINOS_GRAFICA).sort_values("Frecuencia"), "x": "Bigram", "y": "Frecuencia", "titulo": "Combinaciones consecutivas mas frecuentes", "xlabel": "Cantidad de apariciones", "ylabel": "Bigram"}
    }
    for archivo, cfg in config_barras.items():
        _generar_grafica_barras(datos=cfg["datos"], x_col=cfg["x"], y_col=cfg["y"], ruta=graficas_dir / archivo, titulo=cfg["titulo"], xlabel=cfg["xlabel"], ylabel=cfg["ylabel"], xlim=cfg.get("xlim"), con_etiquetas=cfg.get("con_etiquetas", False))
    guardar_nube_palabras(dict(zip(frecuencias["Token"], frecuencias["Frecuencia"])), graficas_dir / ARCHIVOS_GRAFICAS[0])
    guardar_grafica_longitudes(procesados, graficas_dir / ARCHIVOS_GRAFICAS[2])

def mostrar_resultados(calidad, estadisticas, frecuencias, bigramas, patrones):
    secciones = [("CALIDAD Y DISPONIBILIDAD DEL TEXTO", calidad, 0), ("ESTADISTICAS GENERALES DE LOS NOMBRES", estadisticas.T.reset_index(names=["Metrica", "Valor"]), 3), ("FRAGMENTOS ALFABETICOS MAS FRECUENTES", frecuencias.head(TOP_TERMINOS_GRAFICA), 3),
        ("BIGRAMAS MAS FRECUENTES", bigramas.head(TOP_TERMINOS_GRAFICA), 3), ("PATRONES DE FORMATO", patrones, 3)]
    for titulo, tabla, decimales in secciones:
        imprimir_titulo(titulo)
        imprimir_tabla(tabla, decimales=decimales)

def guardar_resultados(csv_dir, tablas): return [(ruta := csv_dir / nombre, tablas[clave].to_csv(ruta, index=False, encoding="utf-8-sig"))[0] for nombre, clave in ARCHIVOS_CSV.items()]

def ejecutar_actividad():
    base_dir = resolver_base_dir()
    resultados_dir = base_dir / CARPETA_RESULTADOS
    csv_dir = base_dir / CARPETA_CSV
    graficas_dir = base_dir / CARPETA_GRAFICAS
    for carpeta in (resultados_dir, csv_dir, graficas_dir):
        carpeta.mkdir(parents=True, exist_ok=True)
    ruta_reporte = resultados_dir / "reporte_act9_analisis_texto.txt"
    with registrar_salida(ruta_reporte):
        imprimir_titulo("ACTIVIDAD 9 - ANALISIS DE TEXTO DE NOMBRES DE USUARIO")
        print(f"Directorio base: {base_dir}")
        print(f"Directorio de resultados: {resultados_dir}")
        print("Fuente textual: data/final/main/jugadores.csv | Variable: jugador_nombre")
        print(f"Longitud minima de fragmento alfabetico: {MINIMO_LONGITUD_TOKEN} caracteres")
        jugadores, calidad_claves = cargar_tablas(base_dir)
        procesados, mascara_valida, tokens_por_nombre, secuencias_bigramas = preparar_nombres(jugadores)
        calidad = crear_resumen_calidad(jugadores, calidad_claves, procesados, mascara_valida)
        estadisticas = crear_estadisticas_texto(procesados)
        frecuencias, bigramas, _ = crear_frecuencias(tokens_por_nombre, secuencias_bigramas, len(procesados))
        patrones = crear_patrones_formato(procesados)
        distribucion = crear_distribucion_longitud(procesados)
        mostrar_resultados(calidad, estadisticas, frecuencias, bigramas, patrones)
        tablas = {"calidad": calidad, "estadisticas": estadisticas, "nombres_procesados": procesados, "frecuencias_tokens": frecuencias, "frecuencias_bigramas": bigramas, "patrones_formato": patrones, "distribucion_longitud": distribucion}
        archivos_csv = guardar_resultados(csv_dir, tablas)
        guardar_graficas(procesados, frecuencias, bigramas, patrones, graficas_dir)
        imprimir_titulo("RESUMEN FINAL")
        print(f"Registros originales: {len(jugadores):,}")
        print(f"Nombres validos analizados: {len(procesados):,}")
        print(f"Fragmentos alfabeticos: {int(estadisticas.loc[0, 'Tokens_alfabeticos_totales']):,}")
        print(f"Fragmentos distintos: {int(estadisticas.loc[0, 'Tokens_alfabeticos_unicos']):,}")
        print(f"Reporte completo: {ruta_reporte}")
        print(f"Directorio CSVs: {csv_dir}")
        print(f"Directorio Graficas: {graficas_dir}")
        print("\nArchivos CSV generados:")
        for ruta in archivos_csv:
            print(f"\t|-> {ruta}")
        print("\nGraficas generadas:")
        for nombre in ARCHIVOS_GRAFICAS:
            print(f"\t|-> {graficas_dir / nombre}")

def main():
    try:
        ejecutar_actividad()
    except Exception as error:
        print(f"\nERROR DURANTE LA EJECUCIÓN: {type(error).__name__}: {error}", file=sys.stderr)
        raise

if __name__ == "__main__":
    main()
