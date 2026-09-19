
# Importación de librerías necesarias
import heapq  # Para manejar la cola de prioridad del algoritmo A*
from math import radians, sin, cos, sqrt, atan2  # Para calcular distancias reales (Haversine)

class AStarRouter:
    """
    Clase que implementa el algoritmo A* para encontrar la ruta óptima
    entre estaciones del metro de Ciudad de México.
    
    El algoritmo A* combina:
    - El costo real desde el inicio (g)
    - Una estimación del costo restante hasta el destino (h - heurística)
    Para minimizar el costo total f = g + h
    """
    
    def __init__(self, graph, positions, station_lines, transfer_penalty=4.0):
        """
        Inicialización del sistema de rutas con A*
        
        Parámetros:
        - graph: Grafo con las conexiones entre estaciones (quién conecta con quién)
        - positions: Posiciones (latitud, longitud) de cada estación
        - station_lines: Qué líneas pasan por cada estación
        - transfer_penalty: Tiempo extra por transbordo en MINUTOS (default: 4.0 min)
                          Incluye: caminar entre andenes + esperar siguiente tren
        """
        self.graph = graph  # Diccionario: estación -> lista de conexiones
        self.pos = positions  # Diccionario: estación -> (latitud, longitud) coordenadas
        self.station_lines = station_lines  # Diccionario: estación -> [líneas que pasan]
        self.transfer_penalty = transfer_penalty  # Tiempo extra en MINUTOS por cambiar de línea

    def heuristic(self, a, b):
        """
        FUNCIÓN HEURÍSTICA: Estimación del tiempo restante desde a hasta b
        
        Calcula el TIEMPO REAL en minutos usando:
        1. Distancia real en km (fórmula de Haversine sobre la Tierra)
        2. Velocidad promedio del Metro CDMX: 35 km/h
        3. Tiempo de parada: 30 segundos (0.5 minutos)
        
        Esta es una estimación optimista que garantiza que A* encuentre la ruta óptima.
        
        Parámetros:
        - a: Estación de origen
        - b: Estación de destino
        
        Retorna: Tiempo estimado en MINUTOS
        """
        # Obtener coordenadas geográficas (latitud, longitud) de las estaciones
        lat1, lon1 = self.pos[a]
        lat2, lon2 = self.pos[b]
        
        # FÓRMULA DE HAVERSINE: Calcula distancia real sobre la superficie terrestre
        R = 6371  # Radio de la Tierra en kilómetros
        
        # Convertir grados a radianes
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        
        # Aplicar fórmula de Haversine
        a_val = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a_val), sqrt(1-a_val))
        distancia_km = R * c
        
        # CONVERTIR DISTANCIA A TIEMPO EN MINUTOS
        velocidad_promedio_kmh = 35  # Velocidad promedio del Metro CDMX
        tiempo_viaje_minutos = (distancia_km / velocidad_promedio_kmh) * 60
        
        # Añadir tiempo de parada en la estación (30 segundos = 0.5 minutos)
        tiempo_parada_minutos = 0.5
        
        # TIEMPO TOTAL = tiempo de viaje + tiempo de parada
        # NOTA: Las distancias entre estaciones del metro suelen ser 0.8-1.5 km
        # Por lo tanto, el tiempo típico será de 2-3 minutos por estación
        return tiempo_viaje_minutos + tiempo_parada_minutos

    def neighbors(self, node):
        """
        OBTENCIÓN DE ESTACIONES VECINAS
        
        Devuelve todas las estaciones a las que se puede llegar directamente
        desde la estación actual (sin transbordos intermedios).
        
        Parámetro:
        - node: Estación actual
        
        Retorna: Lista de diccionarios con información de las conexiones
        """
        return self.graph.get(node, [])

    def reconstruct(self, current, came_from):
        """
        RECONSTRUCCIÓN DEL CAMINO ÓPTIMO
        
        Una vez encontrado el destino, reconstruye el camino completo desde
        el origen hasta el destino siguiendo los pasos guardados.
        
        Es como seguir un rastro de migas de pan de vuelta a casa.
        
        Parámetros:
        - current: Estación final (destino)
        - came_from: Diccionario que guarda de dónde venimos en cada paso
        
        Retorna: Lista ordenada de estaciones desde origen hasta destino
        """
        # Empezar con la estación final
        path = [current]
        # Ir hacia atrás siguiendo el camino
        while current in came_from:
            current = came_from[current]  # Retroceder un paso
            path.append(current)  # Añadir la estación al camino
        # Invertir el camino para que vaya de origen a destino
        path.reverse()
        return path

    def route(self, start, goal):
        """
        ALGORITMO A* - BÚSQUEDA DE LA RUTA ÓPTIMA
        
        Encuentra el camino más corto entre dos estaciones del metro,
        considerando tanto la distancia como los transbordos.
        
        Parámetros:
        - start: Estación de origen
        - goal: Estación de destino
        
        Retorna: 
        - path: Lista de estaciones que forman la ruta óptima
        - cost: Costo total del viaje
        """
        
        # PASO 1: INICIALIZACIÓN DE ESTRUCTURAS DE DATOS
        # Cola de prioridad: guarda estaciones a explorar ordenadas por costo total (f)
        open_set = []
        # Añadir estación inicial con costo 0 y sin línea previa
        heapq.heappush(open_set, (0, start, None))  # (f_score, estación, línea_entrada)
        
        # Diccionario para reconstruir el camino: guarda de dónde venimos
        came_from = {}
        
        # Diccionario de costos g: costo real desde el inicio hasta cada estación
        g_score = {start: 0.0}
        
        # Mejor línea usada para llegar a cada estación
        best_line = {start: None}
        
        # Conjunto de estados ya visitados para no repetir
        visited = set()

        # PASO 2: BUCLE PRINCIPAL - Explorar estaciones hasta encontrar el destino
        while open_set:  # Mientras haya estaciones por explorar
            # Sacar la estación con menor costo estimado total (f = g + h)
            f, current, in_line = heapq.heappop(open_set)
            
            # COMPROBACIÓN DE META: ¿Hemos llegado al destino?
            if current == goal:
                # ¡Encontramos la ruta óptima!
                path = self.reconstruct(current, came_from)
                
                # CALCULAR INFORMACIÓN ADICIONAL SOBRE LA RUTA
                # Contar transbordos y calcular el costo total correctamente
                num_transfers = 0
                prev_line = None
                
                for i in range(len(path) - 1):
                    curr_station = path[i]
                    next_station = path[i + 1]
                    
                    # Encontrar la línea usada en este segmento
                    curr_line = None
                    for edge in self.neighbors(curr_station):
                        if edge["to"] == next_station:
                            curr_line = edge["line"]
                            break
                    
                    # Contar transbordo si cambiamos de línea
                    if prev_line is not None and curr_line != prev_line:
                        num_transfers += 1
                    
                    prev_line = curr_line
                
                # El costo total ya está calculado correctamente en g_score[current]
                # que incluye distancias + penalizaciones por transbordo
                total_cost = g_score[current]
                
                # Calcular costo de transbordos
                transfer_cost = num_transfers * self.transfer_penalty
                
                # Calcular costo de distancia (total - transbordos)
                distance_cost = total_cost - transfer_cost
                
                # Retornar: ruta, costo total, info adicional
                return path, total_cost, {
                    'num_transfers': num_transfers,
                    'distance_cost': distance_cost,
                    'transfer_cost': transfer_cost,
                    'total_cost': total_cost
                }

            # EVITAR REPETICIONES: Si ya visitamos esta estación con esta línea, saltar
            if (current, in_line) in visited:
                continue
            # Marcar como visitada
            visited.add((current, in_line))

            # PASO 3: EXPLORAR ESTACIONES VECINAS
            # Revisar todas las estaciones a las que podemos ir desde aquí
            for edge in self.neighbors(current):
                neighbor = edge["to"]  # Estación vecina
                line = edge["line"]  # Línea de metro que conecta ambas estaciones
                
                # CÁLCULO DEL TIEMPO BASE: Tiempo en minutos entre estaciones
                step = self.heuristic(current, neighbor)
                
                # TIEMPO EXTRA POR TRANSBORDO: Si cambiamos de línea, añadir tiempo extra
                penalty = 0.0
                # Solo aplicar penalización si venimos de una línea y cambiamos a otra
                if in_line is not None and line != in_line:
                    penalty = self.transfer_penalty  # Tiempo extra en MINUTOS por transbordo
                
                # TIEMPO TOTAL TENTATIVO: tiempo actual + tiempo de viaje + tiempo de transbordo
                tentative_g = g_score[current] + step + penalty
                
                # COMPROBACIÓN DE MEJOR RUTA: ¿Es este camino mejor que el anterior?
                if tentative_g < g_score.get(neighbor, float('inf')):
                    # ¡Sí! Actualizar información con este mejor camino
                    came_from[neighbor] = current  # Guardar de dónde venimos
                    g_score[neighbor] = tentative_g  # Actualizar costo real (g)
                    best_line[neighbor] = line  # Guardar la línea usada
                    
                    # CÁLCULO DE f: Costo total estimado = g (real) + h (estimado)
                    fscore = tentative_g + self.heuristic(neighbor, goal)
                    
                    # Añadir vecino a la cola de prioridad para explorarlo después
                    heapq.heappush(open_set, (fscore, neighbor, line))

        # Si llegamos aquí, no hay camino posible entre origen y destino
        return None, float('inf'), None
