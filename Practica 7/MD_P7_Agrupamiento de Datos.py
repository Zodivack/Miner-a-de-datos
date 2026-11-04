"""
████████████████████████████████████████████████████████████████████████████
█  ACTIVIDAD 7 - AGRUPAMIENTO DE DATOS MEDIANTE K-MEANS                    █
████████████████████████████████████████████████████████████████████████████

------------------------------------------------>
DESCRIPCION GENERAL DEL PROGRAMA
------------------------------------------------>
    Esta practica consiste en construir un modelo de agrupamiento mediante
    el uso de KMeans. Para mi caso, se usara para identificar grupos
    similares dentro de las partidas de MCSR Ranked de la temporada 10, sin
    establecer previamente categorias o etiquetas que indiquen a que grupo
    permanecen cada observacion. Para llevar esto acabo se usan las tablas 
    de partidas.csv, partidas_jugadores.csv y cambios_elo.csv, mediante el 
    identificado de la partida y el UUID de cada jugador, conservando el 
    orden de los jugaadores mediante el indice del jugador, reconsuiyendo 
    la informacion de ambos jugadores en una sola observacion.

    A diferencia de la actividad anterior, en esta no se utiliza una variable
    objetivo ni se busca precidir un resultado. En su lugar, se busca utilizar
    caracteristicas numericas de las partidas para que el algoritmo 
    identifique agrupaciones a partir de las distancias(euclidianas) entre
    las observaciones.

    Para la realizacion de la actividad se tomaron como variables numericas 
    principales aquellas que representan la duracion de la partida, el 
    nivel promedio de ELO de los participantes y la diferencia absoluta entre
    sus ELO previos estimados, conservando las estructuras del Overworld y 
    bationes del Nether para estudiar posteriormente la composicion de los
    grupos encontrados.

    En si, el programa comparara diferentes representaciones de las variables
    y distiontos valores de K (numeros de grupos) mediante metricas de 
    evaluacion, para seleccionar la configuracion ideal. Una vez hecha la
    seleccion, se entrena el modelo final con todas las observaciones 
    disponibles y se analizacion los perfiles de los grupos obtenidos-

    Como salida se generan tablas CSV, estadisticas descriptivas,graficas de 
    seleccion y evaluacion, una visualizacion mediante PCA, perfiles de los
    grupos, el modelo entrenado y un reporte TXT con los principales 
    resultados y consideraciones del analisis.

------------------------------------------------>
MODELO DE AGRUPAMIENTO K-MEANS
------------------------------------------------>
    Unidad de analisis:
        -> Una observacion representa una partida.

    Variables utilizadas para el agrupamiento (X):
        -> log_tiempo_resultado.
        -> elo_promedio_previo.
        -> diferencia_elo_previo.

    El ELO previo estimado de cada jugador se reconstruye mediante la 
    expresion: elo_previo_estimado = elo - cambio_elo

    A partir de los dos ELO individuales se generan las siguientes
    caracteristicas:
        -> ELO promedio: elo_promedio_previo = (ELO_1 + ELO_2) / 2
        -> Diferencia absoluta: diferencia_elo_previo = abs(ELO_1 - ELO_2)

        donde; El ELO promedio representa el nivel general de los 
        participantes de una partida, y la Diferencia absoluta describe que tan
        distintos son sus niveles estimados.
    
    La duracion se tranforma mediante la expresion:
        log_tiempo_resultado = log(1 + tiempo_resultado_ms)
    
    Esta transformacion se selecciona despues de comparar la asimetria del 
    tiempo original y la de su representacion logaritmica. Esto se realiza para
    comprimir los valores elevados y reducir la influencia de partidas de una 
    extrema duracion.

    Ademas, se comparan dos configuraciones de variables:
        -> Tiempo log + diferencia ELO original:
           log_tiempo_resultado
           elo_promedio_previo
           diferencia_elo_previo

        -> Tiempo log + diferencia ELO log:
           log_tiempo_resultado
           elo_promedio_previo
           log_diferencia_elo_previo
    
    Todas las variables de las configuraciones se estandarizan mediante
    StandardScaler para que tengan escalas comparables antes de calcular las
    distancias.

    Despues, K-Means utiliza la distancia euclidiana para asignar cada observacion 
    al centroide mas cercano. Para posteriormente, calcula nuevamente los centroides 
    a partir del promedio de las observaciones asignadas y repite el procedimiento 
    hasta que el agrupamiento se estabiliza o alcanza el limite de iteraciones. 
    Debido a que, no se conocen previamente las agrupaciones existentes, se prueban
    diferentes valores de K(grupos) para identificar una configuracion que proporcione 
    grupos relativamente compactos y separados.

------------------------------------------------>
COMPONENTES DENTRO DEL ANALISIS
------------------------------------------------>
    -> Calidad de datos:
        Se verifican las columnas requeridas, claves,  existencia de los registros
        relacionados y la presencia de exactamente dos jugadores con indices
        validos por partida. Del mismo modo, se revisan los valores de ELO faltantes
        o no validos, los tiempos no finitos o no positivos y el estado de completado
        de cada partida.

    -> Preparacion del dataset:
        Se integran las tablas correspondientes mediante las claves correspondientes
        y se calcula una estimacion del ELO previo de ambos jugadores y se construyen
        las variables derivadas de promedio y diferencia absoluta.

    -> Analisis de exploracion:
        Se calcularon estadisticas descriptivas; media, mediana, desviacion estandar,
        cuartiles, valores extremos y asimetria. Ademas, se generan histogramas con la
        finalidad de observar mas graficamente la distribucion del tiempo orginal, su
        transformacion logaritmica, el ELO promedio y la diferencia absoluta de ELO.

    -> Seleccion de la transformacion del tiempo:
        Dada la anterior seccion se compara la asimetria absoluta del tiempo original
        con la obtenida despues de aplicar log1p y se selecciona la representacion que
        presente menor asimetria absoluta. La decision se justifica mediante la reduccion
        observada y su efecto sobre la distribucion de los tiempos.

    -> Comparacion de configuraciones:
        Se prueban dos configuraciones de variables. Donde, ambas utilizan el tiempo
        seleccionado y ELO promedio, pero con la diferencia en que difieren en su en
        la representacion de la diferencia de ELO; un conserva su escala original y la 
        otra utiliza su transformacion logaritmica.

    -> Seleccion del numero de clusters: 
        Se utiliza el metodo del codo para examinar la disminucion de la inercia conforme
        aumenta el numero de grupos, calculando tambien el coeficiente Silhouette para
        medir que tan bien se encuentra separada cada observacion respecto a su propio 
        grupo y a los grupos mas cercanos. Con medidas complementarias se calculan 
        Davies-Bouldin y Calinski-Harabasz para disponer de diferentes perspectivas sobre
        la calidad del agrupamiento.

    -> Entrenamiento:
        Una vez se selecciona la combinacion de variables y el numero de grupos, se vuelve
        a ajustar K-Means para utilizar todas las observaciones disponibles. Generando una
        etiqueta de cluster para cada partida y calculando los centroides correspondientes.

    -> Interpretacion de los grupos:
        Se calculan la cantidad de partidas, tiempo promedio, tiempo mediano, cuartiles,
        ELO promedio y diferencia de ELO para cada grupo. Ademas, analiza la distribucion
        de estructuras de Overworld y tipos de bastiones en el Nether para identificar
        posibles diferencias en la composicion de los grupos.

    -> Visualizacion:
        Se generan graficas del metodo del codo, Silhouette, distribucion del tiempo por 
        grupo y perfiles de las variables. Tambien se utiliza PCA para representar los grupos 
        en dos dimensiones, facilitando la observacion de su distribucion y separacion visual.

------------------------------------------------>
JUSTIFICACION DE DECISIONES TOMADAS
------------------------------------------------>
    ->  Se exluyen las partidas sin completar porque el objetivo consiste en estudiar la
        duracion de encuentros finalizados, el incorporar partidas interrumpidas podria
        mezclar tiempos incompletos con duraciones realies y afectar la interpretacion de
        los grupos.

    ->  Se utiliza el ELO promedio para representar el nivel general de los participantes y la
        diferencia entre sus niveles, de esta forma las caracteristicas no dependen de cual 
        jugador aparece en el registro de la partida.

    ->  El tiempo se transforma mediante log1p dado a que la distribucion normal presenta una
        asimetria positiva considerable, y la tranformacion reduce la influencia de las partidas
        muy largas produciendo una distribucion mas equilibrada.

    ->  Se realiza una comparacion de la diferencia del ELO original y su transformacion logaritmica
        porque ambas representaciones pueden modificar la influencia de los enfrentamientos con
        diferencias grandes en el calculo de las distancias.

    ->  Se utiliza StandardScaler porque K-Means depende de distancias euclidianas, y la
        estandarizacion evita que las diferencias de escala entre las variables dominene 
        injustificadamente la formacion de los grupos.

    ->  Los valores de K se varian entre 2 y 10 para comparar diferentes niveles de agrupamiento y 
        observar como cambia la compactacin y separacion de las observaciones.

    ->  La utilizacion de 20 inicializaciones se realiza con la finalidad de reducir la dependecia
        de una sola posicion inicial de los centroides, y se fija una semilla aleatoria para 
        facilitar la reproducibilidad de los resultados.

    ->  Se emplea Silhouette como criterio principal para seleccionar la configuracion porque esta
        considera tanto la cercania de las observaciones a su propio grupo como su separacion
        respecto a los grupos vecinos.

    ->  Davies-Bouldin y Calinski-Harabasz se incluyen como metricas complementarias, dado que 
        Davies-Bouldin favorece valores menores, mientras que Calinski-Harabasz favorece valores 
        mayores.

    ->  El metodo del codo solo se utiliza para observar la reduccion de la inercia, no se utiliza
        de forma aislada para seleccionar K, ya que la inercia disminuye conforme aumenta el numero
        de grupos.
    
------------------------------------------------>
INTERPRETACION DE RESULTADOS
------------------------------------------------>
    Cuando se validaron los registros, se relaciono a los participantes con sus cambios de ELO y se
    aplicaron los filtros establecidos de la actividad, las partidas pasaron de 50,000 a 23,842
    disponibles para el clustering. Luego, la seleccion de la representacion del tiempo mas adecuada
    mostro que la asimetria original era de 1.9243, mientras que despues de aplicar log1p disminuyo
    a 0.4968, presentando una reduccion del 74%, por lo que se selecciono la del tiempo transformado.
    Posteriormente, se realizo la comparacion de las dos configuraciones de variables y valores 
    diversos de K y la mejor configuracion correspondio a un diferencia de ELO original con un K
    igual a 2, esta obteniendo un coeficiente Silhouette de 0.371633, una inercia de 42073.7353, un 
    indice Davies-Bouldin de 1.030083 y un indice Calinski-Harabasz de 16688.4813, aunque el metodo
    del codo permitio observar la reduccion de la inercia al aumentar K el mayor coeficiente de
    Silhouette se obtuvo con dos grupos, por lo que se selecciono esta configuracion entre las otras.

    El primer grupo (el cluster 0) contiene 9,942 partidas (41.7%), presenta un tiempo promedio de
    12.162 minutos, una mediana de 12.079 minutos, ELO promedio aproximado de 1,607 y diferencia
    media entre los ELO de ambos participantes es de 66.192 puntos. Mientras que, el segundo grupo
    (cluster 1) contiene 13,900 (58.3%), presenta un tiempo promedio de 21.457 minutos, media de
    19.479 minutos, ELO promedio aproximado de 880 puntos y diferencia media entre los ELO de ambos
    participantes es de 44.233 puntos.

    Al comparar ambos grupos se puede apreciar que el grupo 1 concentra partidas de una menor 
    duracion y particiantes con un ELO promedio considerablemente mayor, presentando una diferencia 
    media de ELO mas elevado, por otra parte, el grupo 2 agrupa partidas de mayor duracion y 
    participantes con un ELO primedio menor. Con esto se pueden identificar dos perfiles generales a 
    la hora de los enfrentamientos: Uno caracterizado por partidas mas cortas y un nivel promedio de 
    ELO mas elevado, y otro con partidas mas largas y un nivel promedio de ELO menor. Esta presunta 
    diferencia describe solo el comportamiento de los datos y no demuestra directamente que el ELO 
    provoque una determinada duracion de las partidas.

    Al momento de analizar las estructuras del Overworld se observaron diferencias en su composcion:
    El grupo 1 presenta una distribucion mas equilibrada entre las categorias con aproximadamente 
    un 18.33% de partidas con BURIED_TREASURE y un 20.49% con VILLAGE, por su parte, en el grupo 2
    se observa una mayor presencia de VILLAGE, con aproximadamente un 34.51%, mientras que 
    BURIED_TREASURE representa alrededor del 1.45%. Esto señala que la composicion de las estructuras
    no es identica entre los grupos y puede aportar informacion complementaria para interpretar los
    perfiles. En cambio, la distribucion de los tipos de bastion es muy similar entre los dos grupos, 
    BRIDGE, HOUSING, STABLES y TREASURE representan proporciones cercanas al 25% en cada uno, por lo 
    que no se observa una diferencia descriptiva importante en esta caracteristica.

    En si, con esta actividad se pudieron distinguir dos tipos de perfiles de partidas dentro del
    dataset, partidas de elite y de novatos (por ponerles etiqueta), donde se identifican diferencias 
    principalmente en duracion y nivel promedio de ELO. Ademas, de que las estructuras de Overworld 
    muestran algunas diferencias de composicion entre los grupos, donde el grupo 2 presenta desequilibrio
    en la eleccion de estructura.

"""
from pathlib import Path
from contextlib import contextmanager
import sys
import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import calinski_harabasz_score, davies_bouldin_score, silhouette_score
from sklearn.preprocessing import StandardScaler

"""
████████████████████████████████████████████████████████████████████████████
█  CONSTANTES Y RUTAS DE ARCHIVOS                                          █
████████████████████████████████████████████████████████████████████████████
"""
SEMILLA_ALEATORIA = 26
VALORES_K = range(2, 11)
INICIALIZACIONES = 20
MAX_ITERACIONES = 300
MUESTRA_SILHOUETTE = 5000
MUESTRA_PCA = 8000
ARCHIVO_PARTIDAS = Path("data/final/main/partidas.csv")
ARCHIVO_JUGADORES = Path("data/final/main/partida_jugadores.csv")
ARCHIVO_CAMBIOS_ELO = Path("data/final/aux/cambios_elo.csv")
CARPETA_RESULTADOS = Path("Act_7/resultados")
COLUMNAS_PARTIDAS = ["id_partida", "estructura_overworld", "tipo_bastion_nether", "tiempo_resultado_ms", "partida_sin_completarse"]
COLUMNAS_JUGADORES = ["id_partida", "indice_jugador", "jugador_uuid"]
COLUMNAS_CAMBIOS_ELO = ["id_partida", "jugador_uuid", "cambio_elo", "elo"]
CLAVE_PARTIDA = ["id_partida"]
CLAVE_JUGADOR = ["id_partida", "jugador_uuid"]

"""
████████████████████████████████████████████████████████████████████████████
█  FUNCIONES GENERALES Y REGISTRO DE SALIDA EN CONSOLA Y ARCHIVO TXT       █
████████████████████████████████████████████████████████████████████████████
"""
def imprimir_titulo(texto, ancho=100 ):
    borde = '█' * ancho
    print(f"\n{borde}\n█{texto.upper().center(ancho - 2)}█\n{borde}")

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
    columnas = [" ".join(str(c).split()) for c in df.columns]
    filas = [[" ".join(str(valor).split()) for valor in fila] for fila in df.astype(object).where(df.notna(), "NaN").itertuples(index=False, name=None)]
    anchos = [len(c) for c in columnas]
    for fila in filas:
        for indice, valor in enumerate(fila):
            if len(valor) > anchos[indice]:
                anchos[indice] = len(valor)
    es_numerica = [col in num_cols for col in df.columns]
    separador = "+-" + "-+-".join("-" * a for a in anchos) + "-+"

    def formatear_fila(fila, encabezado=False):
        celdas = [v.rjust(anchos[i]) if (es_numerica[i] and not encabezado) else v.ljust(anchos[i]) for i, v in enumerate(fila)]
        return f"| {' | '.join(celdas)} |"
    
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
    with open(ruta, "w", encoding="utf-8") as archivo:
        salida_original = sys.stdout
        sys.stdout = SalidaDuplicada(salida_original, archivo)
        try:
            yield
        finally:
            sys.stdout = salida_original

def resolver_base_dir():
    ubicacion = Path(__file__).resolve().parent
    directorio_actual = Path.cwd()
    candidatos = list(dict.fromkeys([ubicacion, *ubicacion.parents, directorio_actual, *directorio_actual.parents]))
    archivos = [ARCHIVO_PARTIDAS, ARCHIVO_JUGADORES, ARCHIVO_CAMBIOS_ELO]
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
def normalizar_texto(serie, minusculas=False):
    resultado = serie.astype("string").str.strip().replace(r"^\s*$", pd.NA, regex=True)
    return resultado.str.lower() if minusculas else resultado

def normalizar_booleano(serie):
    texto = serie.astype("string").str.strip().str.lower()
    verdaderos, falsos = {"true", "1", "1.0", "si", "sí", "yes", "verdadero"}, {"false", "0", "0.0", "no", "falso"}
    resultado = pd.Series(pd.NA, index=serie.index, dtype="boolean")
    resultado[texto.isin(verdaderos)] = True
    resultado[texto.isin(falsos)] = False
    return resultado

def cargar_dataset(ruta, nombre, columnas):
    if not ruta.is_file():
        raise FileNotFoundError(f"No se encontró el archivo {nombre}: {ruta}")
    disponibles = pd.read_csv(ruta, nrows=0, encoding="utf-8-sig").columns.tolist()
    if faltantes := [col for col in columnas if col not in disponibles]:
        raise ValueError(f"Faltan columnas en {nombre}: {faltantes}")
    tabla = pd.read_csv(ruta, usecols=columnas, encoding="utf-8-sig", low_memory=False)
    print(f"Archivo: {ruta}\n{nombre:24} {len(tabla):>10,} filas | {len(tabla.columns):>3} columnas")
    return tabla

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

def cargar_tablas(base_dir):
    config_datasets = {
        "partidas": {
            "ruta": base_dir / ARCHIVO_PARTIDAS, "columnas": COLUMNAS_PARTIDAS, "claves": CLAVE_PARTIDA,
            "transformar": lambda df: df.assign(id_partida=normalizar_id(df["id_partida"]), tiempo_resultado_ms=pd.to_numeric(df["tiempo_resultado_ms"], errors="coerce"), partida_sin_completarse=normalizar_booleano(df["partida_sin_completarse"]), estructura_overworld=normalizar_texto(df["estructura_overworld"]), tipo_bastion_nether=normalizar_texto(df["tipo_bastion_nether"]))
        },
        "partida_jugadores": {"ruta": base_dir / ARCHIVO_JUGADORES, "columnas": COLUMNAS_JUGADORES, "claves": CLAVE_JUGADOR, "transformar": lambda df: df.assign(id_partida=normalizar_id(df["id_partida"]), indice_jugador=pd.to_numeric(df["indice_jugador"], errors="coerce"), jugador_uuid=normalizar_texto(df["jugador_uuid"], minusculas=True))},
        "cambios_elo": {"ruta": base_dir / ARCHIVO_CAMBIOS_ELO, "columnas": COLUMNAS_CAMBIOS_ELO, "claves": CLAVE_JUGADOR, "transformar": lambda df: df.assign(id_partida=normalizar_id(df["id_partida"]), jugador_uuid=normalizar_texto(df["jugador_uuid"], minusculas=True), elo=pd.to_numeric(df["elo"], errors="coerce"), cambio_elo=pd.to_numeric(df["cambio_elo"], errors="coerce"))}
    }
    tablas = {}
    for nombre, cfg in config_datasets.items():
        tabla = cargar_dataset(cfg["ruta"], nombre, cfg["columnas"])
        tablas[nombre] = cfg["transformar"](tabla)
    imprimir_titulo("VALIDACION DE CLAVES")
    for nombre, cfg in config_datasets.items():
        validar_claves_unicas(tablas[nombre], nombre, cfg["claves"])
    return tablas["partidas"], tablas["partida_jugadores"], tablas["cambios_elo"]

def mostrar_calidad(partidas, jugadores, cambios):
    tiempo = partidas["tiempo_resultado_ms"].to_numpy(dtype=float, na_value=np.nan)
    finito = np.isfinite(tiempo)
    estado = partidas["partida_sin_completarse"]
    resumen = [
        ("Partidas originales", len(partidas)), ("Partidas con id faltante", int(partidas["id_partida"].isna().sum())), ("Participaciones en partida_jugadores", len(jugadores)), ("Participaciones con clave incompleta", int(jugadores[CLAVE_JUGADOR].isna().any(axis=1).sum())),
        ("Cambios ELO con clave incompleta", int(cambios[CLAVE_JUGADOR].isna().any(axis=1).sum())), ("Cambios con elo faltante", int(cambios["elo"].isna().sum())), ("Cambios con cambio_elo faltante", int(cambios["cambio_elo"].isna().sum())), ("Tiempos faltantes o no finitos (ms)", int((~finito).sum())), 
        ("Tiempos iguales a cero (ms)", int((finito & (tiempo == 0)).sum())), ("Tiempos negativos (ms)", int((finito & (tiempo < 0)).sum())), ("Partidas marcadas sin completar", int(estado.eq(True).fillna(False).sum())), ("Estado de completado desconocido", int(estado.isna().sum()))
    ]
    tabla = pd.DataFrame(resumen, columns=["Indicador", "Cantidad"])
    imprimir_titulo("RESUMEN DE CALIDAD DE LOS DATOS DE ENTRADA")
    imprimir_tabla(tabla, decimales=0)
    return tabla

"""
████████████████████████████████████████████████████████████████████████████
█  CONSTRUCCION DEL CLUSTERING Y ANALISIS                                  █
████████████████████████████████████████████████████████████████████████████
"""
def construir_dataset_clustering(partidas, jugadores, cambios):
    resumen = {"partidas_originales": int(len(partidas))}
    ids_existentes = set(partidas["id_partida"].dropna().astype(int))
    jugadores_validos = jugadores.dropna(subset=["id_partida", "jugador_uuid", "indice_jugador"])
    fuera = ~jugadores_validos["id_partida"].isin(ids_existentes)
    resumen["participaciones_fuera_de_partidas_existentes"] = int(fuera.sum())
    jugadores_validos = jugadores_validos.loc[~fuera]
    cardinalidad = jugadores_validos.groupby("id_partida").agg(numero_filas=("jugador_uuid", "size"), jugadores_unicos=("jugador_uuid", "nunique"), indices_unicos=("indice_jugador", "nunique"), indice_minimo=("indice_jugador", "min"), indice_maximo=("indice_jugador", "max"))
    validas_dos = (cardinalidad["numero_filas"] == 2) & (cardinalidad["jugadores_unicos"] == 2) & (cardinalidad["indices_unicos"] == 2) & (cardinalidad["indice_minimo"] == 0) & (cardinalidad["indice_maximo"] == 1)
    ids_dos = set(cardinalidad.index[validas_dos])
    resumen["partidas_sin_dos_jugadores_con_indices_0_y_1"] = int(len(ids_existentes - ids_dos))
    resumen["partidas_con_dos_jugadores_validos"] = len(ids_dos)
    jugadores_dos = jugadores_validos.loc[jugadores_validos["id_partida"].isin(ids_dos)].sort_values(["id_partida", "indice_jugador"], kind="stable")
    particiones = jugadores_dos.merge(cambios.dropna(subset=CLAVE_JUGADOR)[CLAVE_JUGADOR + ["elo", "cambio_elo"]], on=CLAVE_JUGADOR, how="left", validate="one_to_one", indicator=True)
    particiones["elo_previo_estimado"] = particiones["elo"] - particiones["cambio_elo"]
    valores_elo = particiones[["elo", "cambio_elo", "elo_previo_estimado"]].to_numpy(dtype=float)
    particiones["elo_previo_valido"] = np.isfinite(valores_elo).all(axis=1) & (particiones["elo_previo_estimado"] > 0)
    resumen["participaciones_sin_coincidencia_en_cambios_elo"] = int(particiones["_merge"].ne("both").sum())
    resumen["participaciones_con_elo_previo_no_valido"] = int((~particiones["elo_previo_valido"]).sum())
    ids_dos_elo = set(particiones.groupby("id_partida")["elo_previo_valido"].sum().loc[lambda x: x == 2].index)
    elo_ancho = particiones.loc[particiones["id_partida"].isin(ids_dos_elo)].pivot(index="id_partida", columns="indice_jugador", values="elo_previo_estimado").rename(columns={0: "elo_previo_jugador_1_estimado", 1: "elo_previo_jugador_2_estimado"})
    datos = partidas.merge(elo_ancho.reset_index(), on="id_partida", how="inner", validate="one_to_one")
    tiempo = datos["tiempo_resultado_ms"].to_numpy(dtype=float, na_value=np.nan)
    tiempo_valido = np.isfinite(tiempo) & (tiempo > 0)
    estado = datos["partida_sin_completarse"]
    finalizada = estado.eq(False).fillna(False).to_numpy(dtype=bool)
    resumen.update({
        "partidas_con_dos_elo_previos_validos": int(len(datos)), "partidas_sin_dos_elo_previos_validos": int(len(ids_dos) - len(datos)), "partidas_no_completadas_entre_las_anteriores": int(estado.eq(True).fillna(False).sum()),
        "partidas_con_estado_desconocido_entre_las_anteriores": int(estado.isna().sum()), "partidas_con_tiempo_no_valido_entre_las_anteriores": int((~tiempo_valido).sum()), "partidas_finalizadas_con_tiempo_no_valido": int((finalizada & ~tiempo_valido).sum()), "partidas_no_completadas_con_tiempo_valido": int((~finalizada & tiempo_valido).sum())})
    mascara_final = finalizada & tiempo_valido
    datos_modelo = datos.loc[mascara_final].copy().reset_index(drop=True)
    if datos_modelo.empty:
        raise ValueError("No quedaron partidas completas con tiempo positivo y ambos ELO previos validos.")
    p1 = datos_modelo["elo_previo_jugador_1_estimado"]
    p2 = datos_modelo["elo_previo_jugador_2_estimado"]
    datos_modelo["elo_promedio_previo"] = (p1 + p2) / 2
    datos_modelo["diferencia_elo_previo"] = (p1 - p2).abs()
    datos_modelo["log_tiempo_resultado"] = np.log1p(datos_modelo["tiempo_resultado_ms"])
    datos_modelo["log_diferencia_elo_previo"] = np.log1p(datos_modelo["diferencia_elo_previo"])
    for col in ["estructura_overworld", "tipo_bastion_nether"]:
        categoria = normalizar_texto(datos_modelo[col])
        datos_modelo[col] = categoria.astype(object).where(categoria.notna(), np.nan)
    columnas_finales = ["id_partida", "tiempo_resultado_ms", "log_tiempo_resultado", "elo_previo_jugador_1_estimado", "elo_previo_jugador_2_estimado", "elo_promedio_previo", "diferencia_elo_previo", "log_diferencia_elo_previo", "estructura_overworld", "tipo_bastion_nether"]
    datos_modelo = datos_modelo[columnas_finales]
    resumen.update({"partidas_finales_para_clustering": int(len(datos_modelo)), "partidas_finales_con_tiempo_cero": int((datos_modelo["tiempo_resultado_ms"] == 0).sum()), "partidas_finales_sin_estructura_overworld": int(datos_modelo["estructura_overworld"].isna().sum()), "partidas_finales_sin_tipo_bastion": int(datos_modelo["tipo_bastion_nether"].isna().sum())})
    return datos_modelo, resumen

def crear_resumen_numerico(datos):
    columnas = ["tiempo_resultado_ms", "log_tiempo_resultado", "elo_promedio_previo", "diferencia_elo_previo"]
    sub = datos[columnas].apply(pd.to_numeric, errors="coerce")
    resumen = sub.agg(["count", "mean", "median", "std", "min", lambda x: x.quantile(0.25), lambda x: x.quantile(0.75), "max", "skew"]).T
    resumen.columns = ["Cantidad", "Media", "Mediana", "Desviacion_estandar", "Minimo", "Q1", "Q3", "Maximo", "Asimetria"]
    return resumen.reset_index().rename(columns={"index": "Variable"})

def crear_tabla_frecuencias(datos, columna):
    serie = normalizar_texto(datos[columna]).fillna("SIN_DATO")
    tabla = serie.value_counts().rename_axis("Categoria").reset_index(name="Cantidad")
    tabla["Porcentaje"] = (tabla["Cantidad"] * 100.0) / len(datos)
    return tabla

def guardar_histograma(serie, titulo, etiqueta_x, ruta, bins=40):
    figura, eje = plt.subplots(figsize=(10, 6))
    eje.hist(pd.to_numeric(serie, errors="coerce").dropna(), bins=bins, edgecolor="black", alpha=0.85)
    eje.set(title=titulo, xlabel=etiqueta_x, ylabel="Cantidad de partidas")
    eje.grid(axis="y", alpha=0.25)
    figura.tight_layout()
    figura.savefig(ruta, dpi=180, bbox_inches="tight")
    plt.close(figura)

def guardar_exploracion(datos, resultados_dir):
    resumen = crear_resumen_numerico(datos)
    resumen.to_csv(resultados_dir / "resumen_exploratorio_act7.csv", index=False, encoding="utf-8-sig")
    frecuencias_config = [("estructura_overworld", "frecuencia_estructura_overworld_act7.csv"), ("tipo_bastion_nether", "frecuencia_tipo_bastion_act7.csv")]
    for columna, archivo in frecuencias_config:
        crear_tabla_frecuencias(datos, columna).to_csv(resultados_dir / archivo, index=False, encoding="utf-8-sig")
    graficas_config = [
        ("tiempo_resultado_ms", "Distribución del tiempo de las partidas", "Tiempo de resultado (ms)", "distribucion_tiempo_act7.png"),
        ("log_tiempo_resultado", "Distribución del logaritmo del tiempo", "log(1 + tiempo en ms)", "distribucion_log_tiempo_act7.png"),
        ("elo_promedio_previo", "Distribución del ELO promedio previo", "ELO promedio estimado", "distribucion_elo_promedio_act7.png"),
        ("diferencia_elo_previo", "Distribución de la diferencia de ELO", "Diferencia absoluta de ELO", "distribucion_diferencia_elo_act7.png"),
    ]
    for columna, titulo, etiqueta, archivo in graficas_config:
        guardar_histograma(datos[columna], titulo, etiqueta, resultados_dir / archivo)
    return resumen

def seleccionar_transformacion_tiempo(datos):
    asimetria_original = float(datos["tiempo_resultado_ms"].skew())
    asimetria_log = float(datos["log_tiempo_resultado"].skew())
    abs_orig, abs_log = abs(asimetria_original), abs(asimetria_log)
    reduccion = (100.0 * (abs_orig - abs_log) / abs_orig) if abs_orig > 1e-12 else 0.0
    usar_log = abs_log < abs_orig
    variable = "log_tiempo_resultado" if usar_log else "tiempo_resultado_ms"
    imprimir_titulo("SELECCION DE LA REPRESENTACION DEL TIEMPO")
    print(f"Asimetria del tiempo original: {asimetria_original:.4f}")
    print(f"Asimetria despues de log1p:    {asimetria_log:.4f}")
    print(f"Reduccion absoluta de asimetria: {reduccion:.2f}%")
    if usar_log:
        print("Decision: Se utilizara el tiempo transformado con log1p.\n")
        print("Motivo: El tiempo original presenta una asimetria positiva mayor y una cola hacia partidas muy largas.\nLa transformacion comprime los valores grandes y reduce la influencia de duraciones extremas en las distancias euclidianas.\nLa asimetria disminuye considerablemente, por lo que la representación logaritmica es mas equilibrada.")
    else:
        print("Decision: Se conservara el tiempo en su escala original.\n")
        print("Motivo: La transformacion logaritmica no reduce la asimetria absoluta observada en esta ejecucion.")
    print("La estandarizacion con StandardScaler se aplicará despues; no sustituye a la transformación logarítmica.")
    motivo_texto = "Se selecciono log1p porque redujo la asimetria y comprime la cola de duraciones largas." if usar_log else "Se conservó el tiempo original porque log1p no redujo la asimetría absoluta."
    return variable, {"asimetria_tiempo_original": asimetria_original, "asimetria_tiempo_log": asimetria_log, "reduccion_asimetria_porcentaje": reduccion, "variable_tiempo_seleccionada": variable, "motivo": motivo_texto}

"""
████████████████████████████████████████████████████████████████████████████
█  PREPARACION Y EVALUACION DE K-MEANS                                     █
████████████████████████████████████████████████████████████████████████████
"""
def crear_configuraciones(variable_tiempo):
    nombre_tiempo = "Tiempo log" if variable_tiempo == "log_tiempo_resultado" else "Tiempo original"
    variables_comunes = [variable_tiempo, "elo_promedio_previo"]
    return {f"{nombre_tiempo} + diferencia ELO original": variables_comunes + ["diferencia_elo_previo"], f"{nombre_tiempo} + diferencia ELO log": variables_comunes + ["log_diferencia_elo_previo"]}

def preparar_matriz(datos, variables):
    matriz = datos[variables].to_numpy(dtype=float, copy=False)
    if not np.isfinite(matriz).all():
        raise ValueError(f"Las variables contienen valores no finitos: {variables}")
    escalador = StandardScaler()
    return escalador.fit_transform(matriz), escalador

def evaluar_configuraciones(datos, configuraciones):
    filas = []
    tamannio_muestra = min(MUESTRA_SILHOUETTE, len(datos))
    for nombre, variables in configuraciones.items():
        matriz, _ = preparar_matriz(datos, variables)
        for k in VALORES_K:
            modelo = KMeans(n_clusters=k, random_state=SEMILLA_ALEATORIA, n_init=INICIALIZACIONES, max_iter=MAX_ITERACIONES, algorithm="lloyd")
            etiquetas = modelo.fit_predict(matriz)
            cantidad_clusters = np.unique(etiquetas).size
            if cantidad_clusters == k:
                conteos = np.bincount(etiquetas, minlength=k)
                silhouette = silhouette_score(matriz, etiquetas, sample_size=tamannio_muestra, random_state=SEMILLA_ALEATORIA)
                filas.append({"Configuracion": nombre, "K": k, "Inercia": modelo.inertia_, "Silhouette": silhouette, "Davies_Bouldin": davies_bouldin_score(matriz, etiquetas), "Calinski_Harabasz": calinski_harabasz_score(matriz, etiquetas), "Cluster_minimo": int(conteos.min()), "Cluster_maximo": int(conteos.max())})
                print(f"{nombre} | K={k:2} | Silhouette={silhouette:.5f} | Inercia={modelo.inertia_:.2f}")
            else:
                print(f"CONSIDERACION: K={k} produjo {cantidad_clusters} grupos, estos se omitiran sus metricas.")
    evaluacion = pd.DataFrame(filas)
    if evaluacion.empty:
        raise ValueError("No se pudo evaluar ninguna combinacion de variables y K.")
    return evaluacion

def seleccionar_configuracion(evaluacion):
    validos = evaluacion.replace([np.inf, -np.inf], np.nan).dropna(subset=["Silhouette", "Davies_Bouldin"])
    if validos.empty:
        raise ValueError("No se pudo calcular metricas validas para seleccionar el modelo.")
    return validos.sort_values(by=["Silhouette", "Davies_Bouldin"], ascending=[False, True], kind="stable").iloc[0]

def entrenar_modelo_final(datos, configuracion, k, configuraciones):
    variables = configuraciones[configuracion]
    matriz, escalador = preparar_matriz(datos, variables)
    modelo = KMeans(n_clusters=int(k), random_state=SEMILLA_ALEATORIA, n_init=INICIALIZACIONES, max_iter=MAX_ITERACIONES, algorithm="lloyd")
    etiquetas = modelo.fit_predict(matriz)
    return modelo, escalador, matriz, etiquetas, variables

"""
████████████████████████████████████████████████████████████████████████████
█  PERFIL E INTERPRETACION DE LOS GRUPOS                                   █
████████████████████████████████████████████████████████████████████████████
"""
def crear_perfiles(datos, etiquetas):
    agrupados = datos.assign(cluster=etiquetas, tiempo_resultado_minutos=datos["tiempo_resultado_ms"] / 60000.0)
    perfiles = agrupados.groupby("cluster").agg(
        partidas=("id_partida", "size"), tiempo_promedio_min=("tiempo_resultado_minutos", "mean"), tiempo_mediano_min=("tiempo_resultado_minutos", "median"), tiempo_q1_min=("tiempo_resultado_minutos", lambda s: s.quantile(0.25)),
        tiempo_q3_min=("tiempo_resultado_minutos", lambda s: s.quantile(0.75)), elo_promedio_medio=("elo_promedio_previo", "mean"), elo_promedio_mediano=("elo_promedio_previo", "median"), diferencia_elo_media=("diferencia_elo_previo", "mean"), diferencia_elo_mediana=("diferencia_elo_previo", "median")).reset_index()
    perfiles["porcentaje_partidas"] = (perfiles["partidas"] * 100.0) / len(agrupados)
    distribuciones = {}
    for columna, nombre in [("estructura_overworld", "estructura"), ("tipo_bastion_nether", "bastion")]:
        frecuencias = agrupados[["cluster", columna]].fillna("SIN_DATO").groupby(["cluster", columna], observed=False).size().rename("cantidad").reset_index()
        frecuencias["porcentaje_en_cluster"] = frecuencias["cantidad"] * 100.0 / frecuencias.groupby("cluster")["cantidad"].transform("sum")
        distribuciones[nombre] = frecuencias
    return agrupados, perfiles, distribuciones

def crear_centroides_originales(modelo, escalador, variables):
    centroides = pd.DataFrame(escalador.inverse_transform(modelo.cluster_centers_), columns=variables)
    if "log_tiempo_resultado" in centroides:
        centroides["tiempo_centroide_ms_aprox"] = np.expm1(centroides.pop("log_tiempo_resultado"))
    if "tiempo_resultado_ms" in centroides:
        centroides["tiempo_centroide_ms"] = centroides.pop("tiempo_resultado_ms")
    if "log_diferencia_elo_previo" in centroides:
        centroides["diferencia_elo_centroide_aprox"] = np.expm1(centroides.pop("log_diferencia_elo_previo"))
    if "diferencia_elo_previo" in centroides:
        centroides["diferencia_elo_centroide"] = centroides.pop("diferencia_elo_previo")
    columna_tiempo = "tiempo_centroide_ms_aprox" if "tiempo_centroide_ms_aprox" in centroides else "tiempo_centroide_ms"
    centroides["tiempo_centroide_min_aprox"] = centroides[columna_tiempo] / 60000.0
    centroides.insert(0, "cluster", np.arange(len(centroides)))
    return centroides

"""
████████████████████████████████████████████████████████████████████████████
█  GRAFICAS DE EXPLORACION Y CLUSTERING                                    █
████████████████████████████████████████████████████████████████████████████
"""
def guardar_graficas_exploratorias(datos, resultados_dir):
    graficas = [
        ("tiempo_resultado_ms", "Distribución del tiempo de las partidas", "Tiempo (ms)", "distribucion_tiempo_act7.png"),("log_tiempo_resultado", "Distribución del logaritmo del tiempo", "log(1 + tiempo en ms)", "distribucion_log_tiempo_act7.png"),
        ("elo_promedio_previo", "Distribución del ELO promedio previo", "ELO promedio estimado", "distribucion_elo_promedio_act7.png"), ("diferencia_elo_previo", "Distribución de la diferencia de ELO", "Diferencia absoluta de ELO", "distribucion_diferencia_elo_act7.png"),
    ]
    for columna, titulo, etiqueta, archivo in graficas:
        guardar_histograma(datos[columna], titulo, etiqueta, resultados_dir / archivo)

def guardar_graficas_clustering(evaluacion, datos_cluster, matriz, modelo, variables, configuraciones, resultados_dir):
    nombres = list(configuraciones)
    partes_evaluacion = {nombre: evaluacion[evaluacion["Configuracion"] == nombre].sort_values("K") for nombre in nombres}
#-> Grafica de inercia por metodo del codo 
    figura, eje = plt.subplots(figsize=(10, 6))
    for nombre, parte in partes_evaluacion.items():
        eje.plot(parte["K"], parte["Inercia"], marker="o", label=nombre)
    eje.set(title="Metodo del codo para K-Means", xlabel="Numero de grupos (K)", ylabel="Inercia")
    eje.set_xticks(list(VALORES_K))
    eje.grid(alpha=0.25)
    eje.legend()
    figura.tight_layout()
    figura.savefig(resultados_dir / "seleccion_k_codo_act7.png", dpi=180)
    plt.close(figura)
#-> Grafica de silhouette
    figura, eje = plt.subplots(figsize=(10, 6))
    for nombre, parte in partes_evaluacion.items():
        eje.plot(parte["K"], parte["Silhouette"], marker="o", label=nombre)
    eje.set(title="Coeficiente Silhouette por configuracion y K", xlabel="Numero de grupos (K)", ylabel="Silhouette")
    eje.set_xticks(list(VALORES_K))
    eje.grid(alpha=0.25)
    eje.legend()
    figura.tight_layout()
    figura.savefig(resultados_dir / "seleccion_k_silhouette_act7.png", dpi=180)
    plt.close(figura)
#-> Proyeccion PCA de los clusters
    pca = PCA(n_components=2, random_state=SEMILLA_ALEATORIA)
    coordenadas = pca.fit_transform(matriz)
    centroides_pca = pca.transform(modelo.cluster_centers_)
    rng = np.random.default_rng(SEMILLA_ALEATORIA)
    indices = rng.choice(len(coordenadas), size=min(MUESTRA_PCA, len(coordenadas)), replace=False)
    figura, eje = plt.subplots(figsize=(10, 7))
    dispersion = eje.scatter(coordenadas[indices, 0], coordenadas[indices, 1], c=datos_cluster["cluster"].to_numpy()[indices], cmap="tab10", s=12, alpha=0.55)
    eje.scatter(centroides_pca[:, 0], centroides_pca[:, 1], marker="X", s=220, c="black", edgecolors="white", linewidths=1.2, label="Centroides")
    eje.set(title="Clusters K-Means proyectados mediante PCA", xlabel=f"Componente principal 1 ({pca.explained_variance_ratio_[0]:.1%})", ylabel=f"Componente principal 2 ({pca.explained_variance_ratio_[1]:.1%})")
    figura.colorbar(dispersion, ax=eje, label="Cluster")
    eje.legend()
    eje.grid(alpha=0.2)
    figura.tight_layout()
    figura.savefig(resultados_dir / "clusters_pca_act7.png", dpi=180)
    plt.close(figura)
#-> Grafica de bigotes del tiempo por cluster
    clusters_unicos = sorted(datos_cluster["cluster"].unique())
    grupos = [
        datos_cluster.loc[datos_cluster["cluster"] == cluster, "tiempo_resultado_ms"] / 60000.0
        for cluster in clusters_unicos
    ]
    figura, eje = plt.subplots(figsize=(10, 6))
    eje.boxplot(grupos, tick_labels=clusters_unicos, showfliers=False)
    eje.set_yscale("log")
    eje.set(title="Distribución del tiempo por cluster", xlabel="Cluster", ylabel="Tiempo (minutos, escala logarítmica)")
    eje.grid(axis="y", alpha=0.25)
    figura.tight_layout()
    figura.savefig(resultados_dir / "tiempo_por_cluster_act7.png", dpi=180)
    plt.close(figura)
#-> Perfil promedio de los clusters
    perfil = pd.DataFrame(matriz, columns=variables).assign(cluster=datos_cluster["cluster"].to_numpy()).groupby("cluster")[variables].mean()
    figura, eje = plt.subplots(figsize=(10, 5))
    perfil_vals = perfil.to_numpy()
    imagen = eje.imshow(perfil_vals, aspect="auto", cmap="coolwarm", vmin=-2, vmax=2)
    eje.set_xticks(range(len(variables)), labels=variables, rotation=20, ha="right")
    eje.set_yticks(range(len(perfil)), labels=[f"Cluster {i}" for i in perfil.index])
    eje.set_title("Perfil promedio de los clusters (estandarizadas)")
    for fila in range(perfil_vals.shape[0]):
        for columna in range(perfil_vals.shape[1]):
            eje.text(columna, fila, f"{perfil_vals[fila, columna]:.2f}", ha="center", va="center", fontsize=9)
    figura.colorbar(imagen, ax=eje, label="Promedio estandarizado")
    figura.tight_layout()
    figura.savefig(resultados_dir / "perfil_clusters_act7.png", dpi=180)
    plt.close(figura)

"""
████████████████████████████████████████████████████████████████████████████
█  EXPORTAR LOS RESULTADOS                                                 █
████████████████████████████████████████████████████████████████████████████
"""
def guardar_resultados(datos, datos_cluster, perfiles, distribuciones, centroides, evaluacion, modelo, escalador, variables, configuracion, decision_tiempo, resultados_dir, resumen_numerico, frecuencias_estructura, frecuencias_bastion):
    salidas = {
        "datos_clustering_preparados.csv": datos, "datos_clustering_asignados.csv": datos_cluster, "resumen_exploratorio_act7.csv": resumen_numerico, "frecuencia_estructura_overworld_act7.csv": frecuencias_estructura,
        "frecuencia_tipo_bastion_act7.csv": frecuencias_bastion, "evaluacion_configuraciones_kmeans.csv": evaluacion, "perfil_clusters.csv": perfiles, "distribucion_estructura_por_cluster.csv": distribuciones["estructura"], "distribucion_bastion_por_cluster.csv": distribuciones["bastion"], "centroides_clusters.csv": centroides}
    for nombre, tabla in salidas.items():
        tabla.to_csv(resultados_dir / nombre, index=False, encoding="utf-8-sig")
    joblib.dump({"modelo": modelo, "escalador": escalador, "variables": variables, "configuracion": configuracion, "decision_tiempo": decision_tiempo, "semilla": SEMILLA_ALEATORIA}, resultados_dir / "modelo_kmeans_act7.joblib")

"""
████████████████████████████████████████████████████████████████████████████
█  EJECUCION PRINCIPAL                                                     █
████████████████████████████████████████████████████████████████████████████
"""
def ejecutar_actividad():
    imprimir_titulo("LA EJECUCION DE LA ACTIVIDAD PUEDE TARDAR UN MOMENTO")
    print("\n\n\n")
    base_dir = resolver_base_dir()
    resultados_dir = base_dir / CARPETA_RESULTADOS
    resultados_dir.mkdir(parents=True, exist_ok=True)
    ruta_reporte = resultados_dir / "reporte_act7_kmeans.txt"
    with registrar_salida(ruta_reporte):
        imprimir_titulo("ACTIVIDAD 7 - AGRUPAMIENTO DE PARTIDAS CON K-MEANS")
        print(f"Directorio base: {base_dir}\nDirectorio de resultados: {resultados_dir}\nValores K evaluados: {list(VALORES_K)} | Inicializaciones: {INICIALIZACIONES} | Muestra Silhouette: {MUESTRA_SILHOUETTE:,}")
        imprimir_titulo("CARGA Y VALIDACION DE TABLAS")
        partidas, jugadores, cambios = cargar_tablas(base_dir)
        resumen_calidad = mostrar_calidad(partidas, jugadores, cambios)
        resumen_calidad.to_csv(resultados_dir / "resumen_calidad_entrada_act7.csv", index=False, encoding="utf-8-sig")
        imprimir_titulo("CONSTRUCCION DEL DATASET PARA CLUSTERING")
        datos, resumen_preparacion = construir_dataset_clustering(partidas, jugadores, cambios)
        tabla_resumen = pd.DataFrame([{"Indicador": k.replace("_", " ").capitalize(), "Cantidad": v} for k, v in resumen_preparacion.items()])
        imprimir_tabla(tabla_resumen, decimales=0)
        tabla_resumen.to_csv(resultados_dir / "resumen_preparacion_act7.csv", index=False, encoding="utf-8-sig")
        datos.to_csv(resultados_dir / "datos_clustering_preparados.csv", index=False, encoding="utf-8-sig")
        print(f"\nDataset preparado: {resultados_dir / 'datos_clustering_preparados.csv'}")
        imprimir_titulo("ANALISIS EXPLORATORIO DE LAS VARIABLES")
        resumen_numerico = crear_resumen_numerico(datos)
        imprimir_tabla(resumen_numerico, decimales=3)
        frecuencias_estructura = crear_tabla_frecuencias(datos, "estructura_overworld")
        frecuencias_bastion = crear_tabla_frecuencias(datos, "tipo_bastion_nether")
        guardar_graficas_exploratorias(datos, resultados_dir)
        variable_tiempo, decision_tiempo = seleccionar_transformacion_tiempo(datos)
        configuraciones = crear_configuraciones(variable_tiempo)
        print(f"\nConfiguraciones a evaluar: {list(configuraciones)}")
        imprimir_titulo("EVALUACION DE CONFIGURACIONES Y NUMERO DE CLUSTERS")
        evaluacion = evaluar_configuraciones(datos, configuraciones).sort_values(["Silhouette", "Davies_Bouldin"], ascending=[False, True], kind="stable").reset_index(drop=True)
        imprimir_tabla(evaluacion, decimales=5)
        seleccion = seleccionar_configuracion(evaluacion)
        configuracion, k = seleccion["Configuracion"], int(seleccion["K"])
        imprimir_titulo("CONFIGURACION SELECCIONADA")
        print(f"Configuración: {configuracion} | K: {k}\nSilhouette: {seleccion['Silhouette']:.6f} | Davies-Bouldin: {seleccion['Davies_Bouldin']:.6f} | Calinski-Harabasz: {seleccion['Calinski_Harabasz']:.4f}")
        modelo, escalador, matriz, etiquetas, variables = entrenar_modelo_final(datos, configuracion, k, configuraciones)
        datos_cluster, perfiles, distribuciones = crear_perfiles(datos, etiquetas)
        centroides = crear_centroides_originales(modelo, escalador, variables)
        imprimir_titulo("PERFIL DE LOS CLUSTERS")
        imprimir_tabla(perfiles, decimales=3)
        for nombre, tabla in distribuciones.items():
            imprimir_titulo(f"COMPOSICION POR {nombre.upper()}")
            imprimir_tabla(tabla, decimales=3)
        imprimir_titulo("CENTROIDES EN ESCALAS INTERPRETABLES")
        imprimir_tabla(centroides, decimales=3)
        guardar_graficas_clustering(evaluacion, datos_cluster, matriz, modelo, variables, configuraciones, resultados_dir)
        guardar_resultados(datos, datos_cluster, perfiles, distribuciones, centroides, evaluacion, modelo, escalador, variables, configuracion, decision_tiempo, resultados_dir, resumen_numerico, frecuencias_estructura, frecuencias_bastion)
        imprimir_titulo("RESUMEN FINAL")
        print(f"Partidas originales: {len(partidas):,} | Preparadas y agrupadas: {len(datos_cluster):,}\n")
        print(f"Tiempo seleccionado: {decision_tiempo['variable_tiempo_seleccionada']} | Config: {configuracion} | K: {k}\n")
        print(f"Silhouette: {seleccion['Silhouette']:.6f} | Inercia: {seleccion['Inercia']:.4f}\n\n")
        print(f"Reporte completo: {ruta_reporte}\n")
        print(f"Directorio de resultados: {resultados_dir}\n\n")
        print("Archivos principales generados:")
        archivos_generados = [
            "datos_clustering_preparados.csv", "datos_clustering_asignados.csv","resumen_calidad_entrada_act7.csv", "resumen_preparacion_act7.csv", "resumen_exploratorio_act7.csv", "evaluacion_configuraciones_kmeans.csv", "perfil_clusters.csv", "distribucion_estructura_por_cluster.csv", "distribucion_bastion_por_cluster.csv", "centroides_clusters.csv",
            "modelo_kmeans_act7.joblib", "seleccion_k_codo_act7.png", "seleccion_k_silhouette_act7.png", "clusters_pca_act7.png", "tiempo_por_cluster_act7.png", "perfil_clusters_act7.png", "distribucion_tiempo_act7.png", "distribucion_log_tiempo_act7.png", "distribucion_elo_promedio_act7.png", "distribucion_diferencia_elo_act7.png"
        ]
        for nombre in archivos_generados:
            print(f"\t|-> {resultados_dir / nombre}")

def main():
    try:
        ejecutar_actividad()
    except Exception as error:
        print(f"\nERROR DURANTE LA EJECUCION DE LA PRACTICA 7: {type(error).__name__}: {error}", file=sys.stderr)
        raise

if __name__ == "__main__":
    main()