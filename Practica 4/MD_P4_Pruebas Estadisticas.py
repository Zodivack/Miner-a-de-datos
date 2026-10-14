"""
Checar la independencia de las observaciones
Añadir en justificacion de decisiones porque ademas se añadio estadistica descriptiva especifica y la graficas

████████████████████████████████████████████████████████████████████████████
█  PRUEBAS ESTADISTICAS - MCSR RANKED TEMPORADA 10                         █
████████████████████████████████████████████████████████████████████████████


------------------------------------------------>
DESCRIPCION GENERAL DE PROGRAMA
------------------------------------------------>

Utiliza el dataset final obtenido durante la Practica 1 para evaluar si la
distribucion del tiempo de resultado cambia segun el tipo de bastion del 
Nether o la estructura del Overworld. Para ello, se emplea Kruskal-Wallis 
para resolver ambas cuestiones, mediante la realizacion de una clase propia
que calcula el estadistico H y su correcion por empates; los resultados se
comparan con Scipy utilizando los mismos datos. Asi mismo, se aplica la 
correccion de Holm a las dos pruebas principales y, cuando corresponde,
se realizan comparaciones posteriores de Dunn con ajuste de Holm.

Se generan dos diagramas de caja y bigotes como apoyo visual para comparar
las medianas y la dispercion de distribuciones. Esto solo es para 
complementar la prueba estadistica, no influyen. Para facilitar su lectura
, los puntos atipicos se ocultan en la figura, aunque sus observaciones se
conservan en los calculos estadisticos.

Todo se guarda en un reporte TXT y en archivos CSV que contienen los 
estadisticos de prueba y, si procede, las comparaciones posteriores.

------------------------------------------------>
PRUEBAS ESTADISTICAS A REALIZAR
------------------------------------------------>

-> Prueba 1: Tiempo de resultado segun el tipo de bastion del Nether

    H0: Las distribuciones del tiempo de resultado son iguales entre los 
        tipos de bastion
    
    H1: Al menos un tipo de bastion presenta una distribucion diferente

-> Prueba 2: Tiempo de resultado segun la estructura del Overworld

    H0: Las distribuciones del tiempo de resultado son iguales entre las
        estructura consideradas del Overworld

    H1: Al menos una estructura considerada presenta una distribucion 
        diferente

->  Comparacion adicional: estadistico H y valor p de la implementacion propia
    frente a los obtenidos mediante scipy.stats.kruskal.

->  Comparaciones posteriores: si la prueba global resulta significativa tras
    la correccion de Holm, se emplea Dunn con ajuste de Holm por pares dentro
    del analisis correspondiente.

------------------------------------------------>
JUSTIFICACION DE DECISIONES
------------------------------------------------>

->  Solo se cargara partidas.csv, dado que el tiempo de resultado, el tipo de
    bastion y la estrucutra del Overwold son variables registradas a nivel de
    partida, por lo que no es necesario usar mas tablas

->  Se utiliza tiempo_resultado_segundos como variable numerica de resupuesta
    y se analiza por separado su relacion con cada variable categorica. Esta
    separacion permite estudiar dos preguntas de investigacion diferentes y 
    distinguir sus resultados

->  Se selecciono Kruskal-Wallis debido a la asimetria observada en los
    tiempos y a la presencia de valores extremos. La prueba utiliza rangos 
    y no requiere normalidad, aunque es necesario considerar la independencia
    de las observaciones

->  Se utiliza un nivel de significancia de 0.05. Como se realizan dos pruebas
    principales, se aplicara la correcion de Holm a sus valores p para controlar
    las comparaciones multiples

->  Los diagramas de caja se conservan como complemento visual

->  La implementacion propia calcula los rangos, las sumas de rangos, el
    estadistico H y su correccion por empates. SciPy se utiliza como
    referencia independiente para comprobar los resultados. Esta
    comparacion es complementaria y no sustituye las pruebas principales

->  La independencia no puede garantizarse unicamente con partidas.csv: un 
    jugador puede aparecer en mas de una partida. Esta limitacion se declara
    en el reporte y debe tenerse en cuenta al interpretar los valores p.

->  Un resultado significativo muestra evidencia de diferencias entre las
    distribuciones, pero no demuestra causalidad ni implica por si solo que
    la diferencia sea importante en la practica.
"""
from pathlib import Path
from contextlib import contextmanager
import sys
import numpy as np
import pandas as pd
from scipy.stats import chi2, kruskal, norm
from itertools import combinations
import matplotlib.pyplot as plt

BASE_DIR = Path("MCSR_Ranked")
FINAL_DIR = BASE_DIR / "data" / "final"
MAIN_DIR = FINAL_DIR / "main"
CSV_PARTIDAS = MAIN_DIR / "partidas.csv"

ACT4_DIR = BASE_DIR / "Act_4"
RESULTADOS_DIR = ACT4_DIR / "resultados"
RESULTADOS_DIR.mkdir(parents=True, exist_ok=True)

SALIDA_REPORTE = RESULTADOS_DIR / "reporte_act_4.txt"
SALIDA_PRUEBAS = RESULTADOS_DIR / "resultados_kruskal_wallis.csv"
SALIDA_DUNN_BASTION = RESULTADOS_DIR / "comparaciones_dunn_bastion.csv"
SALIDA_DUNN_ESTRUCTURA = RESULTADOS_DIR / "comparaciones_dunn_estructura.csv"
SALIDA_BOXPLOT_BASTION = RESULTADOS_DIR / "boxplot_tiempo_por_bastion.png"
SALIDA_BOXPLOT_ESTRUCTURA = RESULTADOS_DIR / "boxplot_tiempo_por_estructura.png"

VARIABLE_TIEMPO = "tiempo_resultado_segundos"
VARIABLE_BASTION = "tipo_bastion_nether"
VARIABLE_ESTRUCTURA = "estructura_overworld"
COLUMNAS_REQUERIDAS = [VARIABLE_TIEMPO, VARIABLE_BASTION, VARIABLE_ESTRUCTURA]
ALFA = 0.05
TOLERANCIA_RELATIVA = 1e-9
TOLERANCIA_ABSOLUTA = 1e-12

ETIQUETAS_BASTIONES = {
    "BRIDGE": "Puente",
    "STABLES": "Establos",
    "TREASURE": "Tesoro",
    "HOUSING": "Vivienda"
}
ETIQUETAS_ESTRUCTURAS = {
    "VILLAGE": "Aldea",
    "DESERT_TEMPLE": "Templo del desierto",
    "SHIPWRECK": "Naufragio",
    "RUINED_PORTAL": "Portal en ruinas",
    "BURIED_TREASURE": "Tesoro enterrado"
}

"""
████████████████████████████████████████████████████████████████████████████
█  FUNCIONES GENERALES Y REGISTRO DE SALIDA EN CONSOLA Y ARCHIVO TXT       █
████████████████████████████████████████████████████████████████████████████
"""
def imprimir_titulo(texto):
    print(f"\n{'█' * 100}\n█{f" {texto} ".center(100-2, " ")}█\n{'█' * 100}")

def imprimir_tabla(columnas, filas):
    """Imprime una tabla ASCII alineada sin requerir librerias adicionales."""
    filas_texto = [[str(valor) for valor in fila] for fila in filas]
    anchos = [len(str(columna)) for columna in columnas]
    for fila in filas_texto:
        for indice, valor in enumerate(fila):
            anchos[indice] = max(anchos[indice], len(valor))
    separador = "+-" + "-+-".join("-" * ancho for ancho in anchos) + "-+"

    def es_numerico(valor):
        texto = valor.strip().replace(",", "").replace("%", "")
        try:
            float(texto)
            return True
        except ValueError:
            return False

    def formatear_fila(fila):
        celdas = []
        for indice, valor in enumerate(fila):
            alineado = valor.rjust(anchos[indice]) if es_numerico(valor) else valor.ljust(anchos[indice])
            celdas.append(alineado)
        return "| " + " | ".join(celdas) + " |"
    print(separador)
    print(formatear_fila([str(columna) for columna in columnas]))
    print(separador)
    for fila in filas_texto:
        print(formatear_fila(fila))
    print(separador)

def etiqueta_categoria(variable, categoria, incluir_codigo=True):
    etiqueta = ETIQUETAS_BASTIONES.get(str(categoria), str(categoria)) if variable == VARIABLE_BASTION else ETIQUETAS_ESTRUCTURAS.get(str(categoria), str(categoria)) if variable == VARIABLE_ESTRUCTURA else str(categoria)
    return etiqueta if incluir_codigo and etiqueta == str(categoria) else f"{etiqueta} ({categoria})"

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
def cargar_dataset(ruta, nombre, columnas):
    if not ruta.is_file(): 
        raise FileNotFoundError(f"No se encontro el archivo requerido: {ruta}")
    columnas_disponibles = pd.read_csv(ruta, nrows=0).columns.tolist()
    columnas_faltantes = [columna for columna in columnas if columna not in columnas_disponibles]
    if columnas_faltantes:
        raise ValueError(f"Faltan columnas requeridas en {ruta}: {columnas_faltantes}")
    df = pd.read_csv(ruta, usecols=columnas)
    print(f"Archivo: {ruta}")
    print(f"{nombre:25} {len(df):>10,} filas | {len(df.columns):>2} columnas")
    return df

def cargar_tablas():
    imprimir_titulo("CARGANDO DATASET FINAL")
    return {"partidas": cargar_dataset(CSV_PARTIDAS, "partidas", COLUMNAS_REQUERIDAS)}
 

"""
████████████████████████████████████████████████████████████████████████████
█  PREPARACION DE DATOS                                                    █
████████████████████████████████████████████████████████████████████████████
"""
def crear_grupos(tabla, variable_categorica):
    grupos = {}
    for categoria, grupo in tabla.groupby(variable_categorica, sort=True):
        grupos[str(categoria)] = grupo[VARIABLE_TIEMPO].to_numpy(dtype=float)
    if len(grupos) < 2:
        raise ValueError (f"Se necesitan al menos dos categorias valida en {variable_categorica}")
    return grupos

def preparar_datos_analisis(tablas):
    imprimir_titulo("PREPARANDO DATOS PARA LAS PRUEBAS")
    df = tablas["partidas"].copy()
    df[VARIABLE_TIEMPO] = pd.to_numeric(df[VARIABLE_TIEMPO], errors="coerce")
    for variable in [VARIABLE_BASTION, VARIABLE_ESTRUCTURA]:
        df[variable] = df[variable].astype("string").str.strip()
        df[variable] = df[variable].replace("", pd.NA)
    tiempos = df[VARIABLE_TIEMPO].to_numpy(dtype=float, na_value=np.nan)
    tiempos_finitos = np.isfinite(tiempos)
    mascara_tiempo_valido = pd.Series(tiempos_finitos & (tiempos >= 0), index=df.index)
    
    tabla_bastion = df.loc[mascara_tiempo_valido & df[VARIABLE_BASTION].notna(), [VARIABLE_TIEMPO, VARIABLE_BASTION]].copy()
    tabla_estructura = df.loc[mascara_tiempo_valido & df[VARIABLE_ESTRUCTURA].notna(), [VARIABLE_TIEMPO, VARIABLE_ESTRUCTURA]].copy()
    
    grupos_bastion = crear_grupos(tabla_bastion, VARIABLE_BASTION)
    grupos_estructura = crear_grupos( tabla_estructura, VARIABLE_ESTRUCTURA)
    resumen = {
        "filas_originales": len(df),
        "tiempos_ausentes_o_no_numericos": int(df[VARIABLE_TIEMPO].isna().sum()),
        "tiempos_no_finitos": int((~tiempos_finitos & ~np.isnan(tiempos)).sum()),
        "tiempos_negativos": int((tiempos_finitos & (tiempos < 0)).sum()),
        "tiempos_cero": int((tiempos_finitos & (tiempos == 0)).sum()),
        "categorias_bastion_faltantes": int(df[VARIABLE_BASTION].isna().sum()),
        "categorias_estructura_faltantes": int(df[VARIABLE_ESTRUCTURA].isna().sum()),
        "tiempos_validos": int(mascara_tiempo_valido.sum())
    }
    return {"partidas_preparadas": df, "tabla_bastion": tabla_bastion, "tabla_estructura": tabla_estructura, "grupos_bastion": grupos_bastion, "grupos_estructura": grupos_estructura, "resumen": resumen} 

def mostrar_resumen_preparacion(datos):
    imprimir_titulo("RESUMEN DE CALIDAD DE DATOS")

    resumen = datos["resumen"]
    filas_calidad = [
            ("Filas originales", f"{resumen['filas_originales']:,}"),
            ("Tiempos validos (finitos y >= 0)", f"{resumen['tiempos_validos']:,}"),
            ("Tiempos ausentes o no numericos", f"{resumen['tiempos_ausentes_o_no_numericos']:,}"),
            ("Tiempos no finitos", f"{resumen['tiempos_no_finitos']:,}"),
            ("Tiempos negativos", f"{resumen['tiempos_negativos']:,}"),
            ("Tiempos iguales a cero (conservados)", f"{resumen['tiempos_cero']:,}"),
            ("Partidas sin tipo de bastion", f"{resumen['categorias_bastion_faltantes']:,}"),
            ("Partidas sin estructura del Overworld", f"{resumen['categorias_estructura_faltantes']:,}")
    ]
    imprimir_tabla(["Indicador de calidad", "Cantidad"], filas_calidad)
    analisis = [
            ("MUESTRA: TIEMPO SEGUN BASTION", "tabla_bastion", "grupos_bastion", VARIABLE_BASTION),
            ("MUESTRA: TIEMPO SEGUN ESTRUCTURA DEL OVERWORLD", "tabla_estructura", "grupos_estructura", VARIABLE_ESTRUCTURA)
        ]
    for titulo, clave_tabla, clave_grupos, variable in analisis:
        tabla = datos[clave_tabla]
        grupos = datos[clave_grupos]
        imprimir_titulo(titulo)
        total_original = len(datos["partidas_preparadas"])
        excluidos = total_original - len(tabla)
        print(f"Partidas incluidas: {len(tabla):,} de {total_original:,} ({len(tabla) / total_original:.2%})")
        print(f"Partidas no incluidas en esta prueba: {excluidos:,}")
        print(f"Categorias analizadas: {len(grupos)}")
        frecuencias = tabla[variable].value_counts().sort_values(ascending=False)
        filas_categorias = []
        for categoria, cantidad in frecuencias.items():
            filas_categorias.append((etiqueta_categoria(variable, categoria, incluir_codigo=False), f"{cantidad:,}", f"{cantidad / len(tabla):.2%}"))
        filas_categorias.append(("TOTAL", f"{len(tabla):,}", "100.00%"))
        imprimir_tabla(["Categoria", "Partidas (n)", "% de la muestra"], filas_categorias)

"""
████████████████████████████████████████████████████████████████████████████
█  IMPLEMENTACION PROPIA DE KRUSKAL-WALLIS                                 █
████████████████████████████████████████████████████████████████████████████
"""
def preparar_grupos_validos(grupos):
    muestras = {}
    for nombre, valores in grupos.items():
        serie = pd.to_numeric(pd.Series(valores), errors="coerce").dropna()
        muestra = serie.to_numpy(dtype=float)
        muestra = muestra[np.isfinite(muestra)]
        if muestra.size > 0:
            muestras[str(nombre)] = muestra
    if len(muestras) < 2:
        raise ValueError("Se necesitan al menos dos grupos con observaciones validas.")
    return muestras

class PruebaKruskalWallis:
    def __init__(self, alpha=0.05):
        self.alpha = alpha

    def asignar_rangos(self, valores):
        valores = np.asarray(valores, dtype=float)
        orden = np.argsort(valores, kind="mergesort")
        rangos = np.empty(len(valores), dtype=float)
        inicio = 0
        while inicio < len(orden):
            fin = inicio + 1
            while fin < len(orden) and valores[orden[fin]] == valores[orden[inicio]]:
                fin +=1
            rango_promedio = ((inicio + 1) + fin) / 2
            rangos[orden[inicio:fin]] = rango_promedio
            inicio = fin
        return rangos

    def ejecutar(self, grupos):
        muestras = preparar_grupos_validos(grupos)
        valores_combinados = np.concatenate(list(muestras.values()))
        rangos = self.asignar_rangos(valores_combinados)
        cantidad_total = len(valores_combinados)
        inicio = 0
        sumas_rangos = {}
        tamannios = {}
        for nombre, muestra in muestras.items():
            fin = inicio + len(muestra)
            rangos_grupo = rangos[inicio:fin]
            sumas_rangos[nombre] = float(rangos_grupo.sum())
            tamannios[nombre] = len(muestra)
            inicio = fin
        
        suma_terminos = sum(sumas_rangos[nombre]**2 / tamannios[nombre] for nombre in muestras)
        estadistico_sin_corregir = 12 / (cantidad_total * (cantidad_total + 1)) * suma_terminos - 3 * (cantidad_total + 1)
        _, frecuencias_empates = np.unique(valores_combinados, return_counts=True)
        correccion_empates = 1 - (np.sum(frecuencias_empates ** 3 - frecuencias_empates)/ (cantidad_total ** 3 - cantidad_total))
        grados_libertad = len(muestras) - 1
        if correccion_empates <= 0:
            raise ValueError ("Kruskal-Wallis no puede calcularse: todos los tiempos combinados son identicos.")
        estadistico = max(0.0, estadistico_sin_corregir) / correccion_empates
        valor_p = float(chi2.sf(estadistico, grados_libertad))
        return {
            "estadistico": float(estadistico),
            "grados_libertad": grados_libertad,
            "valor_p": valor_p,
            "alpha": self.alpha,
            "rechazar_h0": valor_p < self.alpha,
            "cantidad_total": cantidad_total,
            "tamanos_grupo": tamannios,
            "sumas_rangos": sumas_rangos,
            "correccion_empates": float(correccion_empates)
        }

def ajustar_p_holm(valores_p):
    valores_p = np.array(valores_p, dtype=float)
    cantidad_pruebas = len(valores_p)
    orden = np.argsort(valores_p)
    ajustados = np.empty(cantidad_pruebas, dtype=float)
    maximo_anterior = 0.0
    for posicion, indice in enumerate(orden):
        valor_ajustado = min(1.0, (cantidad_pruebas - posicion) * valores_p[indice])
        maximo_anterior = max(maximo_anterior, valor_ajustado)
        ajustados[indice] = maximo_anterior
    return ajustados

def calcular_dunn(grupos):
    muestras = preparar_grupos_validos(grupos)
    nombres = list(muestras.keys())
    valores_combinados = np.concatenate(list(muestras.values()))
    prueba = PruebaKruskalWallis()
    rangos = prueba.asignar_rangos(valores_combinados)
    cantidad_total = len(valores_combinados)
    suma_rangos = {}
    tamannios = {}
    incio = 0
    for nombre, muestra in muestras.items():
        fin = incio + len(muestra)
        suma_rangos[nombre] = float(rangos[incio:fin].sum())
        tamannios[nombre] = len(muestra)
        incio = fin
    _, frecuencias_empates = np.unique(valores_combinados, return_counts=True)
    ajuste_empates = np.sum(frecuencias_empates ** 3 - frecuencias_empates)
    varianza_rangos = (cantidad_total * (cantidad_total + 1) / 12 - ajuste_empates / (12 * (cantidad_total - 1))) if cantidad_total > 1 else 0.0
    filas = []
    for grupo_1, grupo_2 in combinations(nombres, 2):
        media_rango_1 = suma_rangos[grupo_1] / tamannios[grupo_1]
        media_rango_2 = suma_rangos[grupo_2] / tamannios[grupo_2]
        denominador = np.sqrt(varianza_rangos * (1 / tamannios[grupo_1] + 1 / tamannios[grupo_2]))
        if denominador <= 0:
            estadistico_z = 0.0
            valor_p = 1.0
        else:
            estadistico_z = (media_rango_1 - media_rango_2) / denominador
            valor_p = float(2 * norm.sf(abs(estadistico_z)))
        filas.append({
            "grupo_1": grupo_1,
            "grupo_2": grupo_2,
            "n_grupo_1": tamannios[grupo_1],
            "n_grupo_2": tamannios[grupo_2],
            "diferencia_rangos_promedio": media_rango_1 - media_rango_2,
            "estadistico_z": float(estadistico_z),
            "valor_p": valor_p
        })
    ajuste_holm = ajustar_p_holm([fila["valor_p"] for fila in filas])
    for indice, fila in enumerate(filas):
        fila["valor_p_holm"] = float(ajuste_holm[indice])
        fila["rechazar_h0"] = bool(ajuste_holm[indice] < ALFA)

    return pd.DataFrame(filas)

"""
████████████████████████████████████████████████████████████████████████████
█  ESTILO Y GRAFICAS DE APOYO                                              █
████████████████████████████████████████████████████████████████████████████
"""
def configurar_estilo_graficas():
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams.update({"figure.dpi": 120, "savefig.dpi": 220, "axes.titlesize": 14, "axes.titleweight": "bold", "axes.labelsize": 11, "xtick.labelsize": 10, "ytick.labelsize": 10})

def generar_boxplot(tabla, variable_categorica, ruta):
    categorias = sorted(tabla[variable_categorica].dropna().unique())
    grupos = [tabla.loc[tabla[variable_categorica] == categoria, VARIABLE_TIEMPO].to_numpy(dtype=float) for categoria in categorias]
    etiquetas = [ETIQUETAS_BASTIONES.get(str(categoria), str(categoria)) if variable_categorica == VARIABLE_BASTION else ETIQUETAS_ESTRUCTURAS.get(str(categoria), str(categoria)) for categoria in categorias]
    fig, ax = plt.subplots(figsize=(10, 7))
    resultado_box = ax.boxplot(grupos, tick_labels=etiquetas, showmeans=True, showfliers=False)
    ax.set_title("Tiempo de resultado por tipo de bastion del Nether" if variable_categorica == VARIABLE_BASTION else "Tiempo de resultado por estructura del Overworld")
    ax.set_xlabel("Categoria")
    ax.set_ylabel("Tiempo de resultado (segundos)")
    ax.grid(axis="y", alpha=0.25)
    ax.tick_params(axis="x", rotation=12)
    fig.subplots_adjust(left=0.10, right=0.98, top=0.90, bottom=0.22)
    fig.legend(handles=[resultado_box["medians"][0], resultado_box["means"][0]], labels=["Mediana", "Media"], loc="lower center", bbox_to_anchor=(0.5, 0.075), ncol=2, frameon=False)
    fig.text(0.5, 0.025, "Los valores extremos individuales se omiten de la figura para facilitar la lectura; tambien se incluyen en la prueba estadistica.", ha="center", va="center", fontsize=8)
    plt.savefig(ruta, dpi=220, bbox_inches="tight")
    plt.close()
    print(f"Diagrama de caja guardado: {ruta}")

"""
████████████████████████████████████████████████████████████████████████████
█  EJECUCION Y REPORTE DE LAS PRUEBAS                                      █
████████████████████████████████████████████████████████████████████████████
"""
def ejecutar_analisis(nombre, tabla, variable_categorica, ruta_grafica):
    imprimir_titulo(nombre)
    print(f"Variable numerica: {VARIABLE_TIEMPO}")
    print(f"Variable categorica: {variable_categorica}")
    print(f"Observaciones utilizadas: {len(tabla):,}")
    generar_boxplot(tabla, variable_categorica, ruta_grafica)
    grupos = crear_grupos(tabla, variable_categorica)
    prueba_propia = PruebaKruskalWallis(alpha=ALFA)
    resultado_propio = prueba_propia.ejecutar(grupos)
    muestras_scipy = preparar_grupos_validos(grupos)
    resultado_scipy = kruskal(*muestras_scipy.values())
    diferencia_h = abs(resultado_propio["estadistico"] - resultado_scipy.statistic)
    diferencia_p = abs(resultado_propio["valor_p"] - resultado_scipy.pvalue)
    coincide_estadistico = np.isclose(resultado_propio["estadistico"], resultado_scipy.statistic, rtol=TOLERANCIA_RELATIVA, atol=TOLERANCIA_ABSOLUTA)
    coincide_valor_p = np.isclose(resultado_propio["valor_p"], resultado_scipy.pvalue, rtol=TOLERANCIA_RELATIVA, atol=TOLERANCIA_ABSOLUTA)
    comparacion_correcta = bool(coincide_estadistico and coincide_valor_p)
    cantidad_total = sum(len(muestra) for muestra in muestras_scipy.values())
    cantidad_grupos = len(muestras_scipy)
    if cantidad_total > cantidad_grupos:
        epsilon_bruto = (float(resultado_scipy.statistic) - cantidad_grupos + 1) / (cantidad_total - cantidad_grupos)
        epsilon_cuadrado = max(0.0, epsilon_bruto)
    else:
        epsilon_bruto = np.nan
        epsilon_cuadrado = np.nan
    print("\nCOMPROBACION DE LA IMPLEMENTACION PROPIA FRENTE A SCIPY")
    filas_comparacion = [
        ("Implementacion propia", f"{resultado_propio['estadistico']:.8f}", f"{resultado_propio['valor_p']:.8g}"),
        ("SciPy", f"{resultado_scipy.statistic:.8f}", f"{resultado_scipy.pvalue:.8g}"),
        ("Diferencia absoluta", f"{diferencia_h:.3e}", f"{diferencia_p:.3e}")
    ]
    imprimir_tabla(["Metodo", "Estadistico H", "Valor p"], filas_comparacion)
    print("Validacion: coincidencia dentro de la tolerancia numerica." if comparacion_correcta else "ADVERTENCIA: los resultados no coinciden; revisar antes de interpretar.")
    return {
        "nombre": nombre,
        "variable_categorica": variable_categorica,
        "tabla": tabla,
        "grupos": grupos,
        "resultado_propio": resultado_propio,
        "resultado_scipy": resultado_scipy,
        "comparacion_correcta": comparacion_correcta,
        "n": int(cantidad_total),
        "k": int(cantidad_grupos),
        "epsilon_cuadrado": float(epsilon_cuadrado),
        "epsilon_bruto": float(epsilon_bruto),
        "valor_p_holm": np.nan,
        "rechazar_h0": False
    }

def mostrar_resultados_globales(resultados):
    imprimir_titulo("RESULTADOS PRINCIPALES Y CORRECCION DE HOLM")
    valores_p = [resultado["resultado_scipy"].pvalue for resultado in resultados]
    valores_p_ajustados = ajustar_p_holm(valores_p)
    filas_resultados = []
    for indice, resultado in enumerate(resultados):
        resultado["valor_p_holm"] = float(valores_p_ajustados[indice])
        resultado["rechazar_h0"] = bool(valores_p_ajustados[indice] < ALFA)
        categoria = "Tipo de bastion" if resultado["variable_categorica"] == VARIABLE_BASTION else "Estructura Overworld"
        decision = "Rechazar H0" if resultado["rechazar_h0"] else "No rechazar H0"
        filas_resultados.append((categoria, f"{resultado['n']:,}", str(resultado["k"]), f"{resultado['resultado_scipy'].statistic:.6f}", f"{resultado['resultado_scipy'].pvalue:.4e}", f"{resultado['valor_p_holm']:.4e}", f"{resultado['epsilon_cuadrado']:.5f}", decision))
    imprimir_tabla(["Analisis", "n", "k", "H", "p sin ajustar", "p Holm", "epsilon^2", "Decision"], filas_resultados)
    print(f"Nivel de significancia: alfa = {ALFA:.2f}")
    print("Decision basada en p ajustado por Holm, no en el valor p sin ajustar.")
    print("epsilon^2 es una medida aproximada del tamano del efecto; las estimaciones negativas se muestran como cero.")
    print("\nINTERPRETACION RESUMIDA")
    for resultado in resultados:
        p_ajustado = resultado["valor_p_holm"]
        if resultado["rechazar_h0"]:
            print(f"- {resultado['nombre']}: p ajustado = {p_ajustado:.4e} < alfa; hay evidencia de diferencias entre las distribuciones.")
        else:
            print(f"- {resultado['nombre']}: p ajustado = {p_ajustado:.4e} >= alfa; no hay evidencia suficiente para afirmar diferencias.")
            if not resultado["comparacion_correcta"]:
                print("  ADVERTENCIA: la comparacion propia frente a SciPy requiere revision.")

def mostrar_comparaciones_dunn(resultado, ruta_salida):
    nombre = resultado["nombre"]
    variable = resultado["variable_categorica"]
    imprimir_titulo(f"COMPARACIONES POSTERIORES DE DUNN: {nombre}")
    tabla_dunn = calcular_dunn(resultado["grupos"])
    tabla_ordenada = tabla_dunn.sort_values("valor_p_holm").reset_index(drop=True)
    
    filas_tabla = []
    for _, fila in tabla_ordenada.iterrows():
        filas_tabla.append((etiqueta_categoria(variable, fila["grupo_1"], incluir_codigo=False), etiqueta_categoria(variable, fila["grupo_2"], incluir_codigo=False), f"{int(fila['n_grupo_1']):,}", f"{int(fila['n_grupo_2']):,}", f"{fila['diferencia_rangos_promedio']:+,.1f}", 
            f"{fila['estadistico_z']:+.3f}", f"{fila['valor_p']:.3e}", f"{fila['valor_p_holm']:.3e}", "Si" if fila["rechazar_h0"] else "No"))
    
    significativas = int(tabla_dunn["rechazar_h0"].sum())
    print(f"Comparaciones por pares: {len(tabla_dunn)}")
    print(f"Pares significativos tras Holm: {significativas} de {len(tabla_dunn)}")
    print("La diferencia de rangos se calcula como promedio del Grupo 1 menos promedio del Grupo 2.")
    print("Una diferencia positiva indica rangos promedio mayores en el Grupo 1; no representa segundos de diferencia.")
    print("Los valores p ajustados por Holm se utilizan para decidir si cada par difiere.")
    imprimir_tabla(["Grupo 1", "Grupo 2", "n1", "n2", "Delta rangos", "Z", "p sin ajuste", "p Holm", "Difiere"], filas_tabla)
    tabla_exportacion = tabla_dunn.copy()
    tabla_exportacion["etiqueta_grupo_1"] = tabla_exportacion["grupo_1"].map(lambda categoria: etiqueta_categoria(variable, categoria, incluir_codigo=False))
    tabla_exportacion["etiqueta_grupo_2"] = tabla_exportacion["grupo_2"].map(lambda categoria: etiqueta_categoria(variable, categoria, incluir_codigo=False))
    tabla_exportacion.to_csv(ruta_salida, index=False, encoding="utf-8-sig")
    print(f"Archivo CSV de comparaciones: {ruta_salida}")

def guardar_resultados_pruebas(resultados):
    filas = []
    for resultado in resultados:
        scipy = resultado["resultado_scipy"]
        filas.append({
            "analisis": resultado["nombre"],
            "variable_categorica": resultado["variable_categorica"],
            "n": resultado["n"],
            "cantidad_grupos": resultado["k"],
            "estadistico_H": float(scipy.statistic),
            "grados_libertad": resultado["k"] - 1,
            "valor_p_sin_ajustar": float(scipy.pvalue),
            "valor_p_holm": resultado["valor_p_holm"],
            "alfa": ALFA,
            "rechazar_H0": resultado["rechazar_h0"],
            "epsilon_cuadrado_aproximado": resultado["epsilon_cuadrado"],
            "coincide_con_SciPy": resultado["comparacion_correcta"]
        })
    pd.DataFrame(filas).to_csv(SALIDA_PRUEBAS, index=False, encoding="utf-8-sig")
    print(f"Resultados de las pruebas guardados: {SALIDA_PRUEBAS}")

def mostrar_limitaciones():
    imprimir_titulo("LIMITACIONES DE INTERPRETACION")
    print("-> Kruskal-Wallis supone independencia entre las observaciones. Como un mismo jugador puede participar en varias partidas, esta condicion podria no cumplirse completamente y el analisis no modela explicitamente esa dependencia.")
    print("-> Un resultado significativo indica diferencias entre las distribuciones, pero no demuestra causalidad ni implica que las diferencias sean importantes en la practica.")
    print("-> La interpretacion de los resultados como diferencias de medianas requiere que las distribuciones de los grupos tengan formas suficientemente similares.")


"""
████████████████████████████████████████████████████████████████████████████
█  EJECUCION DE LA ACTIVIDAD 4                                             █
████████████████████████████████████████████████████████████████████████████
"""
def ejecutar_act4():
    with registrar_salida(SALIDA_REPORTE):
        imprimir_titulo("ACT 4 - PRUEBAS ESTADISTICAS")
        print(f"Nivel de significancia: {ALFA:.2f}")
        tablas = cargar_tablas()
        datos = preparar_datos_analisis(tablas)
        mostrar_resumen_preparacion(datos)
        configurar_estilo_graficas()
        resultados = [
            ejecutar_analisis("TIEMPO SEGUN TIPO DE BASTION", datos["tabla_bastion"], VARIABLE_BASTION, SALIDA_BOXPLOT_BASTION),
            ejecutar_analisis("TIEMPO SEGUN ESTRUCTURA DEL OVERWORLD", datos["tabla_estructura"], VARIABLE_ESTRUCTURA, SALIDA_BOXPLOT_ESTRUCTURA)
        ]
        mostrar_resultados_globales(resultados)
        guardar_resultados_pruebas(resultados)
        rutas_dunn = {VARIABLE_BASTION: SALIDA_DUNN_BASTION, VARIABLE_ESTRUCTURA: SALIDA_DUNN_ESTRUCTURA}
        for resultado in resultados:
            if resultado["rechazar_h0"]:
                mostrar_comparaciones_dunn(resultado, rutas_dunn[resultado["variable_categorica"]])
            else:
                ruta_obsoleta = rutas_dunn[resultado["variable_categorica"]]
                if ruta_obsoleta.exists():
                    ruta_obsoleta.unlink()
                print(f"\nNo se ejecutan comparaciones posteriores para {resultado['nombre']} porque la prueba global no fue significativa tras el ajuste de Holm.")
        mostrar_limitaciones()
        imprimir_titulo("ACTIVIDAD 4 COMPLETADA")
        print("Archivos generados:")
        print(f"|-> Reporte TXT:              {SALIDA_REPORTE}")
        print(f"|-> Resultados Kruskal-Wallis: {SALIDA_PRUEBAS}")
        print(f"|-> Diagrama por bastion:     {SALIDA_BOXPLOT_BASTION}")
        print(f"|-> Diagrama por estructura:  {SALIDA_BOXPLOT_ESTRUCTURA}")
        if SALIDA_DUNN_BASTION.exists():
            print(f"|-> Comparaciones Dunn bastion:    {SALIDA_DUNN_BASTION}")
        if SALIDA_DUNN_ESTRUCTURA.exists():
            print(f"|-> Comparaciones Dunn estructura: {SALIDA_DUNN_ESTRUCTURA}")
    
    return datos

if __name__ == "__main__":
    ejecutar_act4()
