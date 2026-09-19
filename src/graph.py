
# Importación de librería para leer archivos JSON
import json

def load_data(path):
    """
    CARGA DE DATOS DEL METRO DESDE ARCHIVO JSON
    
    Lee toda la información del sistema de metro desde un archivo:
    - Posiciones de estaciones
    - Líneas que pasan por cada estación
    - Conexiones entre estaciones
    - Información de las líneas (colores, recorridos)
    - Estaciones de transbordo
    - Tamaño del lienzo para dibujar
    
    Parámetro:
    - path: Ruta del archivo JSON con los datos
    
    Retorna: Tupla con toda la información del metro
    """
    
    # PASO 1: ABRIR Y LEER EL ARCHIVO JSON
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)  # Cargar datos en formato JSON
    
    # PASO 2: EXTRAER POSICIONES DE ESTACIONES
    # Crear diccionario: nombre_estación -> (latitud, longitud) COORDENADAS GEOGRÁFICAS
    # IMPORTANTE: Usamos "x" e "y" que son las coordenadas geográficas reales,
    # NO "x_coords" y "y_coords" que son coordenadas del canvas en píxeles
    stations = {s["name"]: (s["x"], s["y"]) for s in data["stations"]}
    
    # PASO 3: EXTRAER LÍNEAS POR ESTACIÓN
    # Crear diccionario: nombre_estación -> [lista de líneas que pasan]
    station_lines = {s["name"]: s["lines"] for s in data["stations"]}
    
    # PASO 4: EXTRAER CONEXIONES ENTRE ESTACIONES (GRAFO)
    # Diccionario: estación_origen -> lista de estaciones conectadas con su línea
    edges = {}
    for a, lst in data["edges"].items():
        edges[a] = lst
    
    # PASO 5: EXTRAER INFORMACIÓN DE LAS LÍNEAS
    # Diccionario con colores y recorrido de cada línea
    lines = data["lines"]
    
    # PASO 6: EXTRAER ESTACIONES DE TRANSBORDO
    # Conjunto con nombres de estaciones donde se puede cambiar de línea
    transfers = set(data.get("transfers", []))
    
    # PASO 7: OBTENER DIMENSIONES DEL LIENZO PARA DIBUJAR
    canvas_w, canvas_h = data["canvas_size"]
    
    # Devolver todos los datos procesados
    return stations, station_lines, edges, lines, (canvas_w, canvas_h), transfers

def path_to_segments(path, edges):
    """
    CONVERSIÓN DE RUTA A SEGMENTOS CON INFORMACIÓN DE LÍNEA
    
    Transforma una lista de estaciones (ruta) en segmentos individuales,
    donde cada segmento contiene:
    - Estación de origen
    - Estación de destino
    - Línea de metro utilizada
    
    Esto es útil para dibujar la ruta en el mapa con los colores correctos.
    
    Parámetros:
    - path: Lista ordenada de estaciones de la ruta
    - edges: Diccionario de conexiones entre estaciones
    
    Retorna: Lista de tuplas (origen, destino, línea)
    """
    
    # Lista para almacenar los segmentos
    segs = []
    
    # RECORRER LA RUTA DE ESTACIÓN EN ESTACIÓN
    for i in range(len(path)-1):
        a, b = path[i], path[i+1]  # Estación actual y siguiente
        
        # BÚSQUEDA DE LA LÍNEA UTILIZADA
        # Encontrar qué línea conecta estas dos estaciones
        line = None
        for e in edges.get(a, []):  # Revisar todas las conexiones desde 'a'
            if e["to"] == b:  # Si esta conexión va a 'b'
                line = e["line"]  # Guardar la línea
                break  # Ya encontramos la línea, salir del bucle
        
        # Añadir el segmento con su información
        segs.append((a, b, line))
    
    return segs
