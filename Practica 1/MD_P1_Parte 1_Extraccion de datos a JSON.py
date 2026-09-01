"""
████████████████████████████████████████████████████████████████████████████
█  LIBRERIAS                                                               █
████████████████████████████████████████████████████████████████████████████
"""
import asyncio
import aiohttp
import json
import time
from pathlib import Path

"""
████████████████████████████████████████████████████████████████████████████
█  CONDICIONES INICIALES                                                   █
████████████████████████████████████████████████████████████████████████████
"""
BASE_URL = "https://api.mcsrranked.com"
TEMPORADA_OBJETIVO = 10
TIPO_RANKED = 2
COUNT = 100
LIMITE_PARTIDAS = 50000

# La API tiene una limitacion de 500 peticiones por cada 10 minutos, por lo que se realiza una peticion cada 1.25s
ESPERA_GLOBAL = 1.25
CONCURRENCIA_MAXIMA = 10 

BASE_DIR = Path("MCSR_Ranked")
RAW_DIR = BASE_DIR / "raw"
DETAILS_DIR = BASE_DIR / "details"

RAW_DIR.mkdir(parents=True, exist_ok=True)
DETAILS_DIR.mkdir(parents=True, exist_ok=True)

MATCHES_FILE = RAW_DIR / f"season_{TEMPORADA_OBJETIVO}_matches.jsonl"
DETAILS_FILE = DETAILS_DIR / f"season_{TEMPORADA_OBJETIVO}_details.jsonl"
FAILED_FILE = RAW_DIR / f"season_{TEMPORADA_OBJETIVO}_failed.txt"

PRIVATE_KEY = None
file_lock = asyncio.Lock()

"""
████████████████████████████████████████████████████████████████████████████
█  LIMITAR GLOBALMENTE LA VELOCIDAD                                        █
████████████████████████████████████████████████████████████████████████████
"""
class LimitadorGlobal:
    def __init__(self, delay):
        self.delay = delay
        self.ultima_peticion = 0.0
        self.lock = asyncio.Lock()

    async def esperar(self):
        async with self.lock:
            ahora = time.monotonic()
            tiempo_transcurrido = ahora - self.ultima_peticion

            if tiempo_transcurrido < self.delay:
                await asyncio.sleep(self.delay - tiempo_transcurrido)

            self.ultima_peticion = time.monotonic()

limitador = LimitadorGlobal(ESPERA_GLOBAL)

"""
████████████████████████████████████████████████████████████████████████████
█  FUNCIONES AUXILIARES                                                    █
████████████████████████████████████████████████████████████████████████████
"""
def asegurar_limite_archivo(ruta_archivo, limite):
    if not ruta_archivo.exists():
        return
        
    with open(ruta_archivo, "r", encoding="utf-8") as f:
        lineas = f.readlines()
    
    if len(lineas) > limite:
        exceso = len(lineas) - limite
        print(f"\n[LIMPIEZA] El archivo tiene {len(lineas):,} partidas.")
        print(f"[LIMPIEZA] Eliminando las últimas {exceso:,} para mantener exactamente {limite:,}...")
        
        with open(ruta_archivo, "w", encoding="utf-8") as f:
            f.writelines(lineas[:limite])
            
        print("[LIMPIEZA] Archivo recortado con éxito.\n")

def guardar_jsonl(path, objeto):
    with open(path, "a", encoding="utf-8") as archivo:
        archivo.write(json.dumps(objeto, ensure_ascii=False) + "\n")

def guardar_id_fallido(path, match_id):
    with open(path, "a", encoding="utf-8") as archivo:
        archivo.write(f"{match_id}\n")

def cargar_ids_existentes(path):
    ids = set()

    if not path.exists():
        return ids
    
    with open(path, "r", encoding="utf-8") as archivo:
        for linea in archivo:
            try:
                registro = json.loads(linea)

                if "id" in registro:
                    ids.add(str(registro["id"]))

            except json.JSONDecodeError:
                continue
    return ids

def cargar_partidas():
    partidas = []

    if not MATCHES_FILE.exists():
        return partidas
    
    with open(MATCHES_FILE, "r", encoding="utf-8") as archivo:
        for linea in archivo:
            try:
                partidas.append(json.loads(linea))
            except json.JSONDecodeError:
                continue
    return partidas

"""
████████████████████████████████████████████████████████████████████████████
█  PETICION HTTP                                                           █
████████████████████████████████████████████████████████████████████████████
"""
async def solicitar_async(session, url, params=None, reintentos=5):
    for intento in range(1, reintentos + 1):
        try:
            await limitador.esperar()
            
            async with session.get(url, params=params, timeout=30) as response:
                if response.status == 429:
                    espera = 60 * intento
                    print(f"\n[429] Límite rebasado. Esperando {espera}s...")
                    await asyncio.sleep(espera)
                    continue

                response.raise_for_status()
                data = await response.json()

                if data.get("status") != "success":
                    raise RuntimeError(f"Respuesta inesperada:\n{data}")
                return data["data"]
                
        except Exception as error:
            if intento < reintentos:
                await asyncio.sleep(10 * intento)
            else:
                print(f"Fallo definitivo en {url}: {error}")
                return None
    return None
"""
████████████████████████████████████████████████████████████████████████████
█  DESCARGAR PARTIDAS                                                      █
████████████████████████████████████████████████████████████████████████████
"""
async def descargar_partidas_temporada(session):
    print("\n" + "=" * 70)
    print(f"DESCARGANDO PARTIDAS DE LA TEMPORADA {TEMPORADA_OBJETIVO}")
    print("=" * 70)
    partidas_guardadas = cargar_partidas()
    ids_existentes = {str(p["id"]) for p in partidas_guardadas}
    
    if ids_existentes:
        print(f"Se encontraron {len(ids_existentes):,} partidas ya descargadas.")
        
        if len(ids_existentes) >= LIMITE_PARTIDAS:
            print(f"\n¡Ya se alcanzó el límite establecido de {LIMITE_PARTIDAS:,} partidas! Saltando descarga de nuevas.")
            return
        before = partidas_guardadas[-1]["id"]
        print(f"Reanudando la búsqueda desde el cursor: before={before}")
    else:
        print("No existen datos previos. Comenzando desde cero.")
        before = None

    pagina = 0

    while True:
        pagina += 1
        params = {"count": COUNT, "type": TIPO_RANKED, "season": TEMPORADA_OBJETIVO}
        if before is not None:
            params["before"] = before

        print(f"Página {pagina} | Cursor before={before}")
        matches = await solicitar_async(session, f"{BASE_URL}/matches", params=params)

        if not matches:
            print("La API no devolvió más partidas.")
            break
        temporadas_en_pagina = []
        limite_alcanzado = False

        for match in matches:
            season = match.get("season")
            match_id = str(match.get("id"))
            temporadas_en_pagina.append(season)

            if season != TEMPORADA_OBJETIVO:
                continue
            if match_id in ids_existentes:
                continue

            guardar_jsonl(MATCHES_FILE, match)
            ids_existentes.add(match_id)

            if len(ids_existentes) >= LIMITE_PARTIDAS:
                limite_alcanzado = True
                break

        print(f"-> Partidas de temporada {TEMPORADA_OBJETIVO} acumuladas: {len(ids_existentes):,}")

        if limite_alcanzado:
            print(f"\n¡Se ha alcanzado el límite de {LIMITE_PARTIDAS:,} partidas configurado! Terminando paginación.")
            break

        temporadas_validas = [s for s in temporadas_en_pagina if s is not None]

        if temporadas_validas and max(temporadas_validas) < TEMPORADA_OBJETIVO:
            print(f"\nYa pasamos completamente la temporada {TEMPORADA_OBJETIVO}. Terminando paginación.")
            break

        nuevo_before = matches[-1].get("id")

        if nuevo_before is None or before == nuevo_before:
            print("El cursor no avanzó o no se pudo obtener. Terminando para evitar bucle.")
            break

        before = nuevo_before

"""
████████████████████████████████████████████████████████████████████████████
█  IMPLEMENTACION DE WORKERS PARA DESCARGAR DETALLES DE FORMA CONCURRENTE  █
████████████████████████████████████████████████████████████████████████████
"""
async def worker(nombre, session, cola, progreso):
    while True:
        match_id = await cola.get()

        if match_id is None:
            cola.task_done()
            break
            
        detalle = await solicitar_async(session, f"{BASE_URL}/matches/{match_id}")
        
        if detalle:
            async with file_lock:
                guardar_jsonl(DETAILS_FILE, detalle)
            progreso["completados"] += 1

        else:
            async with file_lock:
                guardar_id_fallido(FAILED_FILE, match_id)
            progreso["errores"] += 1

        total_actual = progreso["completados"] + progreso["errores"]
        
        if total_actual % 100 == 0:
            porcentaje = (total_actual / progreso["total"]) * 100
            print(f"[{nombre}] {total_actual:,} / {progreso['total']:,} ({porcentaje:.1f}%) procesados (Éxito: {progreso['completados']} | Errores: {progreso['errores']})")
            
        cola.task_done()

"""
████████████████████████████████████████████████████████████████████████████
█  DESCARGA DE DETALLES                                                    █
████████████████████████████████████████████████████████████████████████████
"""
async def descargar_detalles(session):
    print("\n" + "=" * 70)
    print("DESCARGANDO DETALLES AVANZADOS (WORKER POOL)")
    print("=" * 70)

    partidas = cargar_partidas()
    detalles_existentes = cargar_ids_existentes(DETAILS_FILE)
    pendientes = [str(m["id"]) for m in partidas if str(m["id"]) not in detalles_existentes]

    print(f"Partidas totales a revisar (tras limpieza): {len(partidas):,}")
    print(f"Detalles ya guardados: {len(detalles_existentes):,}")
    print(f"Pendientes por descargar: {len(pendientes):,}\n")

    if not pendientes:
        print("¡Todos los detalles están al día!")
        return

    cola = asyncio.Queue()
    progreso = {"completados": 0, "errores": 0, "total": len(pendientes)}

    for match_id in pendientes:
        cola.put_nowait(match_id)

    workers = [
        asyncio.create_task(worker(f"Worker-{i+1}", session, cola, progreso))
        for i in range(CONCURRENCIA_MAXIMA)
    ]

    await cola.join()

    for _ in workers:
        await cola.put(None)
    await asyncio.gather(*workers)

"""
████████████████████████████████████████████████████████████████████████████
█  MAIN                                                                    █
████████████████████████████████████████████████████████████████████████████
"""
async def main():
    inicio = time.time()
    
    asegurar_limite_archivo(MATCHES_FILE, LIMITE_PARTIDAS)
    headers = {"User-Agent": "MCSR-Ranked-Dataset-Extractor/3.0"}

    if PRIVATE_KEY:
        headers["Private-Key"] = PRIVATE_KEY

    async with aiohttp.ClientSession(headers=headers) as session:
        await descargar_partidas_temporada(session)
        await descargar_detalles(session)

    tiempo_total = time.time() - inicio
    print("\n" + "=" * 70)
    print(f"PROCESO COMPLETO EN {tiempo_total / 60:.2f} MINUTOS")
    print("=" * 70)
    print("Archivos generados:")
    print(f"  - Matches: {MATCHES_FILE}")
    print(f"  - Detalles: {DETAILS_FILE}")
    if FAILED_FILE.exists():
        print(f"  - Fallidos: {FAILED_FILE}")

if __name__ == "__main__":
    asyncio.run(main())