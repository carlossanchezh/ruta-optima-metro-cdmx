# Instrucciones de instalación y ejecución

## Requisitos

- **Python** 3.8 o superior
- **IDE** recomendado

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/carlossanchezh/ruta-optima-metro-cdmx.git
```

## Ejecución

### Desde la línea de comandos

1. Accede al directorio donde haya sido clonado el proyecto

2. Ejecuta la aplicación:
   
```bash
python3 src/app.py
```

> En Windows:

```bash
python src/app.py
```

### Desde un IDE

1. Abre el proyecto en tu IDE.

2. Asegúrate de que el intérprete de Python esté correctamente configurado.

3. Ejecuta el archivo principal `src/app.py`.

## Configuración del Programa

El programa permite ajustar dinámicamente el tiempo de penalización por transbordo desde la propia interfaz gráfica. No es necesario modificar el código para cambiar este parámetro.

Sin embargo, si se desea cambiar el valor por defecto, se puede editar en src/app.py, en la inicialización:

```python
# Valor por defecto: 4.0 minutos
self.router = AStarRouter(edges, self.stations_geo, station_lines, transfer_penalty=4.0)
```

>Si se modifica este valor, basta con volver a ejecutar la aplicación.

## Uso de la interfaz gráfica

Al iniciar la aplicación se abre una ventana con:

**Origen** — menú desplegable para seleccionar la estación de partida.

**Destino** — menú desplegable para seleccionar la estación de llegada.

**Tiempo de transbordo** (minutos) — control numérico para ajustar la penalización por cambio de línea (por defecto 4.0).

**Calcular ruta** (A*) — ejecuta el algoritmo y muestra la ruta óptima.

**Limpiar** — borra los resultados y reinicia las selecciones.

**Mapa del metro** — lienzo que muestra la red completa y resalta la ruta calculada.

**Área de texto** — muestra el desglose de tiempos (viaje, transbordos, total) y la lista de paradas.

