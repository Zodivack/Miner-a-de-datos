"""
████████████████████████████████████████████████████████████████████████████
█  LIBRERIAS                                                               █
████████████████████████████████████████████████████████████████████████████
"""
import json
import csv
import pandas as pd
from pathlib import Path

"""
████████████████████████████████████████████████████████████████████████████
█  CONDICIONES INICIALES                                                   █
████████████████████████████████████████████████████████████████████████████
"""
TEMPORADA_OBJETIVO = 10
BASE_DIR = Path("MCSR_Ranked")
RAW_DIR = BASE_DIR / "raw"
DETAILS_DIR = BASE_DIR / "details"
PROCESSED_DIR = BASE_DIR / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
MATCHES_FILE = RAW_DIR / f"season_{TEMPORADA_OBJETIVO}_matches.jsonl"
DETAILS_FILE = DETAILS_DIR / f"season_{TEMPORADA_OBJETIVO}_details.jsonl"
CSV_PRINCIPAL = PROCESSED_DIR / f"mcsr_ranked_season_{TEMPORADA_OBJETIVO}.csv"
CSV_AUXILIAR = PROCESSED_DIR / f"mcsr_ranked_season_{TEMPORADA_OBJETIVO}_aux.csv"
TEMP_PRINCIPAL = PROCESSED_DIR / f"temp_principal_{TEMPORADA_OBJETIVO}.jsonl"
TEMP_AUXILIAR = PROCESSED_DIR / f"temp_auxiliar_{TEMPORADA_OBJETIVO}.jsonl"

"""
████████████████████████████████████████████████████████████████████████████
█  FUNCIONES AUXILIARES                                                    █
████████████████████████████████████████████████████████████████████████████
"""
def aplanar_diccionario(diccionario, prefijo=""):
    plano = {}
    for llave, valor in diccionario.items():
        nombre = f"{prefijo}{llave}"
        
        if isinstance(valor, dict):
            plano.update(aplanar_diccionario(valor, f"{nombre}_"))
        elif isinstance(valor, list):
            continue
        else:
            plano[nombre] = valor
            
    return plano

def extraer_listas(objeto, match_id, ruta="", filas=None, indice_padre=None):
    if filas is None:
        filas = []

    if isinstance(objeto, dict):
        for llave, valor in objeto.items():
            nueva_ruta = f"{ruta}.{llave}" if ruta else llave

            if not isinstance(valor, list):
                if isinstance(valor, dict):
                    extraer_listas(valor, match_id, nueva_ruta, filas, indice_padre)
                continue

            for indice, elemento in enumerate(valor):
                if nueva_ruta == "timelines":
                    filas.append({
                        "match_id": match_id,
                        "tipo_dato": "timelines",
                        "indice": indice,
                        "player_uuid": elemento.get("uuid"),
                        "time": elemento.get("time"),
                        "type": elemento.get("type")
                    })
                    continue
                if nueva_ruta == "players":
                    filas.append({
                        "match_id": match_id,
                        "tipo_dato": "players",
                        "indice": indice,
                        "player_uuid": elemento.get("uuid"),
                        "nickname": elemento.get("nickname"),
                        "roleType": elemento.get("roleType"),
                        "eloRate": elemento.get("eloRate"),
                        "eloRank": elemento.get("eloRank"),
                        "country": elemento.get("country")
                    })
                    continue
                if nueva_ruta == "changes":
                    filas.append({
                        "match_id": match_id,
                        "tipo_dato": "changes",
                        "indice": indice,
                        "player_uuid": elemento.get("uuid"),
                        "change": elemento.get("change"),
                        "eloRate": elemento.get("eloRate")
                    })
                    continue
                fila = {
                    "match_id": match_id,
                    "tipo_dato": nueva_ruta,
                    "indice": indice
                }

                if isinstance(elemento, dict):
                    datos = aplanar_diccionario(elemento)
                    for campo, dato in datos.items():
                        fila[campo] = dato

                    if "uuid" in elemento:
                        fila["player_uuid"] = elemento["uuid"]
                else:
                    fila["valor"] = elemento

                filas.append(fila)

    elif isinstance(objeto, list):
        for indice, elemento in enumerate(objeto):
            if isinstance(elemento, dict):
                extraer_listas(elemento, match_id, ruta, filas, indice)
            else:
                filas.append({
                    "match_id": match_id,
                    "tipo_dato": ruta,
                    "indice": indice,
                    "valor": elemento
                })
    return filas

"""
████████████████████████████████████████████████████████████████████████████
█  CREAR DATASETS                                                          █
████████████████████████████████████████████████████████████████████████████
"""
def crear_csvs():
    print("=" * 70)
    print("CONVIRTIENDO MCSR RANKED A 2 CSV (OPTIMIZADO EN DISCO & SIN DUPLICADOS)")
    print("=" * 70)
    print("\n1. Indexando detalles...")
    detalles_dict = {}

    if DETAILS_FILE.exists():
        with open(DETAILS_FILE, "r", encoding="utf-8") as archivo:
            for linea in archivo:
                if not linea.strip(): continue
                try:
                    detalle = json.loads(linea)
                    match_id = str(detalle.get("id"))
                    detalles_dict[match_id] = detalle
                except json.JSONDecodeError:
                    continue

    print(f"Detalles indexados: {len(detalles_dict):,}")
    print("\n2. Procesando partidas y escribiendo al disco...")

    if not MATCHES_FILE.exists():
        print("No se encontró el archivo de partidas.")
        return

    with open(MATCHES_FILE, "r", encoding="utf-8") as archivo, \
         open(TEMP_PRINCIPAL, "w", encoding="utf-8") as f_princ, \
         open(TEMP_AUXILIAR, "w", encoding="utf-8") as f_aux:

        for numero, linea in enumerate(archivo, start=1):
            if not linea.strip(): continue
            try:
                match = json.loads(linea)
            except json.JSONDecodeError:
                continue

            match_id = str(match.get("id"))
            detalle = detalles_dict.get(match_id, {})
            fila_principal = {}
            datos_match = aplanar_diccionario(match)
            fila_principal.update(datos_match)
            
            jugadores = match.get("players", [])
            for indice, jugador in enumerate(jugadores, start=1):
                if not isinstance(jugador, dict): continue
                datos_jugador = aplanar_diccionario(jugador)
                for campo, valor in datos_jugador.items():
                    fila_principal[f"player_{indice}_{campo}"] = valor

            datos_detalle = aplanar_diccionario(detalle)
            for campo, valor in datos_detalle.items():
                if campo not in fila_principal:
                    fila_principal[campo] = valor

            f_princ.write(json.dumps(fila_principal, ensure_ascii=False) + "\n")

            listas_match = extraer_listas(match, match_id)
            listas_detalle = extraer_listas(detalle, match_id)
            filas_vistas = set()

            for fila in listas_match:
                fila["origen"] = "match"
                fila_comparacion = json.dumps(
                    {clave: valor for clave, valor in fila.items() if clave != "origen"},
                    sort_keys=True,
                    ensure_ascii=False
                )
                if fila_comparacion in filas_vistas:
                    continue

                filas_vistas.add(fila_comparacion)
                f_aux.write(json.dumps(fila, ensure_ascii=False) + "\n")

            for fila in listas_detalle:
                fila["origen"] = "detail"
                fila_comparacion = json.dumps(
                    {clave: valor for clave, valor in fila.items() if clave != "origen"},
                    sort_keys=True,
                    ensure_ascii=False
                )

                if fila_comparacion in filas_vistas:
                    continue

                filas_vistas.add(fila_comparacion)
                f_aux.write(json.dumps(fila, ensure_ascii=False) + "\n")

            if numero % 5000 == 0:
                print(f"Procesadas: {numero:,}")
    detalles_dict.clear()

    """
    ████████████████████████████████████████████████████████████████████████████
    █  CREAR CSV PRINCIPAL                                                     █
    ████████████████████████████████████████████████████████████████████████████
    """
    print("\n3. Construyendo CSV principal...")
    df_principal = pd.read_json(TEMP_PRINCIPAL, lines=True)

    if df_principal.empty:
        print("No se generaron datos para el CSV principal.")
        return

    if "date" in df_principal.columns:
        df_principal["date_readable"] = pd.to_datetime(
            df_principal["date"], unit="s", errors="coerce",utc=True
        ).dt.strftime('%Y-%m-%d %H:%M:%S')
        
        df_principal = df_principal.sort_values("date").reset_index(drop=True)

    df_principal.to_csv(CSV_PRINCIPAL, index=False, encoding="utf-8-sig")

    """
    ████████████████████████████████████████████████████████████████████████████
    █  CREAR CSV AUXILIAR                                                      █
    ████████████████████████████████████████████████████████████████████████████
    """

    print("4. Mapeando columnas dinámicas del CSV auxiliar...")
    columnas_auxiliares = set()

    with open(TEMP_AUXILIAR, "r", encoding="utf-8") as f_aux:
        for linea in f_aux:
            fila = json.loads(linea)
            columnas_auxiliares.update(fila.keys())

    columnas_base = ["match_id", "origen", "tipo_dato", "indice"]
    columnas_extra = sorted([col for col in columnas_auxiliares if col not in columnas_base])
    todas_las_columnas = columnas_base + columnas_extra
    print("5. Escribiendo CSV auxiliar (Bajo consumo de RAM)...")

    with open(TEMP_AUXILIAR, "r", encoding="utf-8") as f_in, \
         open(CSV_AUXILIAR, "w", encoding="utf-8-sig", newline="") as f_out:

        writer = csv.DictWriter(f_out, fieldnames=todas_las_columnas)
        writer.writeheader()

        for linea in f_in:
            fila = json.loads(linea)
            writer.writerow(fila)

    if TEMP_PRINCIPAL.exists(): TEMP_PRINCIPAL.unlink()
    if TEMP_AUXILIAR.exists(): TEMP_AUXILIAR.unlink()

    print("\n" + "=" * 70)
    print("¡CONVERSIÓN COMPLETADA!")
    print("=" * 70)
    print("\nComprobando integridad...")
    
    ids_originales = set()

    with open(MATCHES_FILE, "r", encoding="utf-8") as archivo:
        for linea in archivo:
            if not linea.strip(): continue
            try:
                match = json.loads(linea)

                if match.get("id") is not None:
                    ids_originales.add(str(match["id"]))

            except json.JSONDecodeError:
                continue

    ids_csv = set(df_principal["id"].astype(str))
    faltantes = ids_originales - ids_csv
    duplicados = df_principal["id"].duplicated().sum()

    print(f"IDs originales en JSONL : {len(ids_originales):,}")
    print(f"IDs resultantes en CSV  : {len(ids_csv):,}")
    print(f"Partidas faltantes      : {len(faltantes):,}")
    print(f"IDs duplicados en CSV   : {duplicados:,}")
    print(f"\nCSV PRINCIPAL")
    print(f"Filas generadas: {len(df_principal):,}")
    print(f"Columnas: {len(df_principal.columns):,}")
    print(f"Archivo: {CSV_PRINCIPAL}")
    print(f"\nCSV AUXILIAR")

    with open(CSV_AUXILIAR, "r", encoding="utf-8") as f:
        filas_aux_totales = sum(1 for _ in f) - 1
        
    print(f"Filas generadas: {filas_aux_totales:,}")
    print(f"Columnas: {len(todas_las_columnas):,}")
    print(f"Archivo: {CSV_AUXILIAR}")
    print("=" * 70)

if __name__ == "__main__":
    crear_csvs()