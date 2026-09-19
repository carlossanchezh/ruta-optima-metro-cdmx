
# ============================================================================
# APLICACIÓN DE BÚSQUEDA DE RUTAS EN EL METRO DE CIUDAD DE MÉXICO
# Usando el algoritmo A* para encontrar el camino óptimo
# ============================================================================

# Importación de librerías necesarias
import tkinter as tk  # Para crear la interfaz gráfica
from tkinter import ttk, messagebox  # Widgets mejorados y ventanas de mensajes
from a_star import AStarRouter  # Nuestro algoritmo A*
from graph import load_data, path_to_segments  # Funciones para cargar y procesar datos

class MetroApp(tk.Tk):
    """
    APLICACIÓN PRINCIPAL - INTERFAZ GRÁFICA DEL METRO CDMX
    
    Esta clase crea la ventana principal con:
    - Selectores de origen y destino
    - Visualización del mapa del metro
    - Resultados de la búsqueda de ruta
    - Botones para calcular y limpiar
    """
    
    def __init__(self):
        """
        INICIALIZACIÓN DE LA APLICACIÓN
        
        Configura la ventana, carga los datos del metro y prepara la interfaz
        """
        # Inicializar la ventana principal
        super().__init__()
        self.title("CDMX A* - Ruta óptima (Práctica IA 2025-26)")
        self.geometry("1600x1000")  # Tamaño de ventana ampliado para mejor visualización

        # CARGA DE DATOS DEL METRO
        # Leer toda la información desde el archivo JSON
        stations, station_lines, edges, lines, (W,H), transfers = load_data("src/data/stations.json")
        
        # Guardar coordenadas GEOGRÁFICAS originales para los cálculos de distancia
        self.stations_geo = stations  # Coordenadas geográficas (latitud, longitud) REALES
        
        # Guardar datos como atributos de la clase para usarlos después
        self.station_lines = station_lines  # Líneas que pasan por cada estación
        self.edges = edges  # Conexiones entre estaciones
        self.lines = lines  # Información de las líneas (color, recorrido)
        self.canvas_size = (W,H)  # Tamaño del área de dibujo
        self.transfers = transfers  # Estaciones de transbordo

        # --- USAR COORDENADAS DEL CANVAS DESDE EL JSON ---
        # Las coordenadas x_coords e y_coords ya están definidas en el JSON
        # para posicionar las estaciones en el canvas
        
        # Cargar las coordenadas del canvas desde el JSON
        with open("src/data/stations.json", "r", encoding="utf-8") as f:
            import json
            json_data = json.load(f)
        
        # Crear diccionario con coordenadas del canvas
        stations_canvas = {}
        for s in json_data["stations"]:
            stations_canvas[s["name"]] = (s["x_coords"], s["y_coords"])

        # Guardar las coordenadas del canvas para dibujar
        self.stations_pos = stations_canvas

        # --- FIN DEL ESCALADO ---

        # CREACIÓN DEL SISTEMA DE RUTAS (Algoritmo A*)
        # CRÍTICO: Usar coordenadas GEOGRÁFICAS, no las del canvas
        # Inicializar el motor de búsqueda con penalización de 4.0 minutos por transbordo
        self.router = AStarRouter(edges, self.stations_geo, station_lines, transfer_penalty=4.0)

        # CONSTRUCCIÓN DE LA INTERFAZ GRÁFICA
        self._build_ui()

    def _build_ui(self):
        """
        CONSTRUCCIÓN DE LA INTERFAZ DE USUARIO
        
        Crea todos los elementos visuales: botones, listas desplegables,
        área de texto, mapa, etc.
        """
        
        # ========== PANEL IZQUIERDO: CONTROLES ==========
        # Crear panel lateral para los controles
        left = ttk.Frame(self)
        left.pack(side="left", fill="y", padx=10, pady=10)

        # SELECTOR DE ESTACIÓN DE ORIGEN
        ttk.Label(left, text="Origen").pack(anchor="w")
        self.origin_var = tk.StringVar()  # Variable para guardar la selección
        self.origin_cb = ttk.Combobox(left, textvariable=self.origin_var, width=40)
        # Llenar con todas las estaciones ordenadas alfabéticamente
        self.origin_cb["values"] = sorted(self.stations_pos.keys())
        self.origin_cb.pack(pady=4)

        # SELECTOR DE ESTACIÓN DE DESTINO
        ttk.Label(left, text="Destino").pack(anchor="w")
        self.dest_var = tk.StringVar()  # Variable para guardar la selección
        self.dest_cb = ttk.Combobox(left, textvariable=self.dest_var, width=40)
        # Llenar con todas las estaciones ordenadas alfabéticamente
        self.dest_cb["values"] = sorted(self.stations_pos.keys())
        self.dest_cb.pack(pady=4)

        # CONTROL DE TIEMPO DE TRANSBORDO
        # Permite ajustar cuántos MINUTOS extra toma hacer un transbordo
        ttk.Label(left, text="Tiempo de transbordo (minutos)").pack(anchor="w", pady=(8,0))
        self.penalty_var = tk.DoubleVar(value=4.0)  # Valor por defecto: 4.0 minutos
        ttk.Spinbox(left, from_=0.0, to=10.0, increment=0.5, textvariable=self.penalty_var, width=10).pack(pady=4)

        # BOTONES DE ACCIÓN
        # Botón para calcular la ruta usando A*
        ttk.Button(left, text="Calcular ruta (A*)", command=self.calculate).pack(pady=10, fill="x")
        # Botón para limpiar la pantalla
        ttk.Button(left, text="Limpiar", command=self.clear).pack(pady=2, fill="x")

        # INSTRUCCIONES PARA EL USUARIO
        ttk.Label(left, text="Instrucciones:").pack(anchor="w", pady=(10,0))
        instr = ("1) Selecciona origen y destino\n"
                 "2) Ajusta tiempo de transbordo (min)\n"
                 "3) Pulsa 'Calcular'\n\n"
                 "Los tiempos se calculan con velocidad\n"
                 "promedio de 35 km/h del Metro CDMX.")
        ttk.Label(left, text=instr, wraplength=280).pack(anchor="w")

        # ÁREA DE RESULTADOS
        # Cuadro de texto para mostrar la ruta calculada
        ttk.Label(left, text="Ruta:").pack(anchor="w", pady=(10,0))
        self.result_text = tk.Text(left, width=45, height=18, wrap="word")
        self.result_text.pack()

        # ========== PANEL DERECHO: MAPA DEL METRO ==========
        # Crear panel para el lienzo de dibujo
        right = ttk.Frame(self)
        right.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # LIENZO PARA DIBUJAR EL MAPA
        # Aquí se dibuja toda la red del metro y la ruta calculada
        self.canvas = tk.Canvas(right, width=self.canvas_size[0], height=self.canvas_size[1], bg="white")
        self.canvas.pack(fill="both", expand=True)
        
        # Dibujar la red completa del metro al iniciar
        self.draw_network()

    def draw_network(self, path=None):
        """
        DIBUJO DEL MAPA DEL METRO
        
        Dibuja toda la red del metro incluyendo:
        - Líneas de metro con sus colores
        - Estaciones
        - Estaciones de transbordo (con círculo extra)
        - Ruta calculada (si existe)
        
        Parámetro:
        - path: Lista de segmentos de la ruta a resaltar (opcional)
        """
        
        # LIMPIAR EL LIENZO
        # Borrar todo lo dibujado anteriormente
        self.canvas.delete("all")
        
        # PASO 1: DIBUJAR TODAS LAS LÍNEAS DEL METRO
        # Recorrer cada línea y dibujar sus conexiones
        for lid, info in self.lines.items():
            color = info["color"]  # Color de la línea
            st = info["stations"]  # Lista de estaciones de la línea
            
            # Dibujar conexiones entre estaciones consecutivas
            for i in range(len(st)-1):
                a, b = st[i], st[i+1]  # Estación actual y siguiente
                ax, ay = self.stations_pos[a]  # Coordenadas de 'a'
                bx, by = self.stations_pos[b]  # Coordenadas de 'b'
                # Dibujar línea entre estaciones con el color correspondiente
                self.canvas.create_line(ax, ay, bx, by, fill=color, width=6, capstyle="round")

        # PASO 2: MARCAR ESTACIONES DE TRANSBORDO
        # Dibujar un círculo extra alrededor de las estaciones donde se puede cambiar de línea
        for name in self.transfers:
            x, y = self.stations_pos[name]
            # Círculo más grande para indicar transbordo
            self.canvas.create_oval(x-12, y-12, x+12, y+12, outline="#333", width=3)

        # PASO 3: RESALTAR LA RUTA CALCULADA (si existe)
        if path:
            # Dibujar cada segmento de la ruta con un borde negro y color de línea
            for (a, b, line) in path:
                ax, ay = self.stations_pos[a]
                bx, by = self.stations_pos[b]
                color = self.lines[line]["color"] if line in self.lines else "black"
                
                # Primero dibujar línea gruesa negra (borde)
                self.canvas.create_line(ax, ay, bx, by, fill="black", width=10, capstyle="round")
                # Luego dibujar línea de color encima (destacar la ruta)
                self.canvas.create_line(ax, ay, bx, by, fill=color, width=6, capstyle="round")

        # PASO 4: DIBUJAR TODAS LAS ESTACIONES
        # Las estaciones se dibujan al final para que queden encima de las líneas
        for name, (x, y) in self.stations_pos.items():
            r = 6  # Radio del círculo de la estación
            # Dibujar círculo blanco con borde negro para cada estación
            self.canvas.create_oval(x-r, y-r, x+r, y+r, fill="white", outline="#111", width=2)
            # Dibujar nombre de la estación
            self.canvas.create_text(x+12, y-12, text=name, anchor="w", font=("TkDefaultFont", 9))

    def calculate(self):
        """
        CÁLCULO DE LA RUTA ÓPTIMA
        
        Se ejecuta cuando el usuario pulsa el botón "Calcular ruta (A*)"
        
        Proceso:
        1. Obtener origen y destino seleccionados
        2. Validar que los datos sean correctos
        3. Ejecutar el algoritmo A*
        4. Mostrar resultados en pantalla
        5. Dibujar la ruta en el mapa
        """
        
        # PASO 1: OBTENER ESTACIONES SELECCIONADAS
        start = self.origin_var.get().strip()  # Estación de origen
        goal = self.dest_var.get().strip()  # Estación de destino
        
        # PASO 2: VALIDACIÓN DE DATOS
        # Comprobar que se han seleccionado ambas estaciones
        if not start or not goal:
            messagebox.showwarning("Faltan datos", "Selecciona origen y destino.")
            return
        
        # Comprobar que no sean la misma estación
        if start == goal:
            messagebox.showinfo("Ruta vacía", "Origen y destino son la misma estación.")
            return

        # PASO 3: CONFIGURAR Y EJECUTAR ALGORITMO A*
        # Actualizar la penalización por transbordo según el valor seleccionado
        self.router.transfer_penalty = float(self.penalty_var.get())
        
        # Ejecutar el algoritmo A* para encontrar la ruta óptima
        path, cost, info = self.router.route(start, goal)
        
        # Comprobar si se encontró una ruta
        if not path:
            messagebox.showerror("Sin ruta", "No se encontró camino.")
            return

        # PASO 4: PROCESAR RESULTADOS
        # Convertir la lista de estaciones en segmentos con información de línea
        segs = path_to_segments(path, self.edges)
        
        # PASO 5: MOSTRAR RESULTADOS EN EL ÁREA DE TEXTO CON DESGLOSE DETALLADO
        self.result_text.delete("1.0", "end")  # Limpiar texto anterior
        self.result_text.insert("end", f"═══════════════════════════════════\n")
        self.result_text.insert("end", f"  Ruta óptima: {start} → {goal}\n")
        self.result_text.insert("end", f"═══════════════════════════════════\n\n")
        
        # Mostrar desglose de tiempos
        self.result_text.insert("end", f"⏱️ DESGLOSE DE TIEMPOS:\n")
        self.result_text.insert("end", f"\n")
        self.result_text.insert("end", f"  • Tiempo de viaje: {info['distance_cost']:.2f} min\n")
        self.result_text.insert("end", f"  • Número de transbordos: {info['num_transfers']}\n")
        self.result_text.insert("end", f"  • Tiempo de transbordos: {info['transfer_cost']:.2f} min\n")
        self.result_text.insert("end", f"    (penalización: {self.router.transfer_penalty:.1f} min/transbordo)\n")
        self.result_text.insert("end", f"\n")
        self.result_text.insert("end", f"  🎯 TIEMPO TOTAL: {info['total_cost']:.2f} minutos\n")
        self.result_text.insert("end", f"  🕒 Aproximadamente: {int(info['total_cost'])} min {int((info['total_cost'] % 1) * 60)} seg\n")
        self.result_text.insert("end", f"\n")
        self.result_text.insert("end", f"─────────────────────────────────\n")
        self.result_text.insert("end", f"\n📍 PARADAS ({len(path)} estaciones):\n\n")
        
        # Listar todas las estaciones de la ruta
        for i, st in enumerate(path):
            self.result_text.insert("end", f"  {i+1}. {st}\n")

        # PASO 6: DIBUJAR LA RUTA EN EL MAPA
        self.draw_network(segs)

    def clear(self):
        """
        LIMPIEZA DE LA PANTALLA
        
        Se ejecuta cuando el usuario pulsa el botón "Limpiar"
        
        Acciones:
        - Borra los resultados del área de texto
        - Limpia las selecciones de origen y destino
        - Redibuja el mapa sin ruta resaltada
        """
        
        # Borrar texto de resultados
        self.result_text.delete("1.0", "end")
        
        # Limpiar selecciones de estaciones
        self.origin_var.set("")
        self.dest_var.set("")
        
        # Redibujar el mapa sin ruta destacada
        self.draw_network()

# ============================================================================
# PUNTO DE ENTRADA DEL PROGRAMA
# ============================================================================
if __name__ == "__main__":
    # Crear la aplicación
    app = MetroApp()
    # Iniciar el bucle principal de la interfaz gráfica
    app.mainloop()
