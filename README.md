# Ruta óptima en la red de metro de Ciudad de México

## Descripción

Este proyecto desarrollado en **Python** calcula la ruta óptima entre dos estaciones del Metro de la Ciudad de México. Utiliza el algoritmo de búsqueda informada **A*** para minimizar el tiempo de viaje, teniendo en cuenta no solo la distancia entre estaciones, sino también el tiempo de penalización por realizar transbordos entre líneas.

La heurística utiliza la fórmula de Haversine para calcular distancias geográficas reales y estima tiempos basados en la velocidad promedio del metro (35 km/h) y tiempos de parada.

La herramienta cuenta con una interfaz gráfica interactiva que permite visualizar el mapa de la red, seleccionar estaciones de origen y destino, y ajustar dinámicamente el tiempo de penalización por transbordo.

## Arquitectura

### Módulos Principales

`a_star.py` (Lógica de Búsqueda):

- Contiene la clase `AStarRouter`.

- **Algoritmo**: Implementa la función de evaluación **$f(n) = g(n) + h(n)$**
  - **$g(n)$**: Coste real acumulado (tiempo de viaje + penalizaciones por transbordo).
  - **$h(n)$**: Heurística (distancia en línea recta convertida a tiempo, garantizando optimalidad).

- **Gestión de Estado**: Utiliza una cola de prioridad (heapq) para explorar los nodos con menor coste estimado primero.

`graph.py` (Gestión de Datos):

- Funciones `load_data` y `path_to_segments`.

- Se encarga de parsear el archivo `stations.json`.

- Transforma la información cruda en estructuras de datos eficientes (diccionarios y listas) para el grafo.

`app.py` (Interfaz Gráfica):
- Contiene la clase `MetroApp`.

- Gestiona la ventana, los controles y el lienzo (`Canvas`).

- Conecta las acciones del usuario con el motor de búsqueda y actualiza la visualización.

### Estructura de Datos

Los datos se almacenan en un archivo JSON con la siguiente estructura:
- `lines`: Información de cada línea (color, nombre, lista de estaciones).

- `stations`: Lista de estaciones con:
  - Coordenadas geográficas reales para cálculos de distancia.
  - Coordenadas de pantalla para el dibujo en el canvas.
  - Líneas a las que pertenece.

- `edges`: Grafo de adyacencia que define las conexiones directas entre estaciones y la línea utilizada.

- `transfers`: Lista de estaciones donde es posible realizar un cambio de línea.

### Funcionamiento

El programa sigue un flujo de ejecución claro que va desde la carga inicial de datos hasta la visualización de la ruta calculada. A continuación se describen las funciones y módulos involucrados en cada etapa.

#### 1. Inicialización del sistema

- Al ejecutar `app.py`, el método `MetroApp.__init__()` crea la ventana principal y configura todos los elementos de la interfaz gráfica.

- La función `load_data()` de `graph.py` lee el archivo `src/data/stations.json` y extrae las estaciones, líneas, aristas, transbordos y el tamaño del canvas.

- Desde `app.py` se cargan las coordenadas del canvas (`x_coords`, `y_coords`) para el dibujo y las coordenadas geográficas (`x, y`) para los cálculos de distancia.

- Se instancia el motor de búsqueda con `AStarRouter.__init__()` de `a_star.py`, pasándole el grafo, las posiciones geográficas y la penalización por transbordo.

- Finalmente, `draw_network()` dibuja la red completa del metro en el canvas: líneas con sus colores, estaciones y círculos de transbordo.

#### 2. Cálculo de ruta (acción del usuario)

- Cuando el usuario pulsa "Calcular ruta (A*)", se ejecuta el método `calculate()` de `app.py`, que primero valida que se hayan seleccionado origen y destino.

- Luego se llama a `AStarRouter.route()` en `a_star.py`, que ejecuta el algoritmo A*. Internamente, esta función utiliza:
  - `heuristic(a, b)`: calcula la distancia Haversine entre dos estaciones y la convierte a tiempo estimado en minutos.

  - `neighbors(node)`: obtiene las estaciones vecinas conectadas directamente.

  - `reconstruct(current, came_from)`: una vez encontrado el destino, reconstruye la ruta óptima desde el origen.

- Después, `path_to_segments()` de `graph.py` convierte la lista de estaciones en segmentos con información de la línea utilizada, necesaria para dibujar con los colores correctos.

- `draw_network(path)` de `app.py` redibuja el mapa resaltando la ruta calculada con líneas gruesas (borde negro más color de línea).

- Finalmente, `calculate()` de `app.py` muestra en el área de texto el desglose de tiempos, el número de transbordos, el tiempo total y la lista de paradas. 

#### 3. Limpieza de pantalla

- Al pulsar "Limpiar", se ejecuta el método `clear()` de `app.py`, que borra el texto de resultados, limpia las selecciones de origen y destino, y redibuja el mapa sin ruta resaltada llamando de nuevo a `draw_network()`.

### Tecnologías

- Lenguaje: **Python**
- Interfaz Gráfica: **Tkinter** (Librería estándar de Python).
- Estructuras de Datos: **JSON**
- Algoritmos: **A***, **Fórmula de Haversine**

## Estructura del proyecto

```plaintext
.
├── assets/
│  └── MapaMetroCDMX.png            # Imagen del mapa de metro
│ 
├── docs/
│   └── CoordenadasParadasCDMX.md   # Coordenadas reales de cada parada
│ 
├── src/
│   ├── a_star.py                   # Implementación del algoritmo A* y heurística
│   ├── app.py                      # Punto de entrada y lógica de la interfaz gráfica (UI)
│   ├── graph.py                    # Carga de datos y utilidades del grafo
│   └── data/
│       └── stations.json           # Base de datos con estaciones, coordenadas y conexiones
│ 
├── README.md                       # Descripción del proyecto
└── requirements.txt                # Requerimientos de instalación para python
```
