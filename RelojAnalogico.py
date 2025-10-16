# reloj_analogico_multizona.py
# Rolex-like clock con cambio de estilos y ciudades (1 a la vez)

import tkinter as tk
import math
import time
from datetime import datetime, timezone, timedelta

# ----- Configuración -----
WIDTH, HEIGHT = 480, 640
CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2 - 40
RADIUS = 200

# Estilos completos (fondos + agujas)
STYLES = {
    "Negro": {
        "bg": "#0b0b0b",
        "dial": "#070707",
        "marks": "#e9e9e9",
        "hour": "#dcdcdc",
        "minute": "#f8f8f8",
        "second": "#ff5555",
        "gmt": "#aaaaee"
    },
    "Verde": {
        "bg": "#002b1f",
        "dial": "#380066",
        "marks": "#e9e9e9",
        "hour": "#ffffff",
        "minute": "#ccffcc",
        "second": "#ff3333",
        "gmt": "#66ff66"
    },
    "Morado": {
        "bg": "#2b003f",
        "dial": "#002b66",
        "marks": "#f0f0f0",
        "hour": "#ba66ff",
        "minute": "#ba66ff",
        "second": "#38014e",
        "gmt": "#9c33ff"
    }
}

# Ciudades importantes (offset respecto UTC)
WORLD_CITIES = {
    "Bogotá": -5,
    "New York": -4,
    "London": 0,
    "Tokyo": 9
}

# ----- Utilidades -----
def polar_to_cart(cx, cy, radius, angle_degrees):
    """Convierte coordenadas polares (grados) a cartesianas (x,y)"""
    angle_radians = math.radians(angle_degrees - 90)  # 0 grados arriba
    x = cx + radius * math.cos(angle_radians)
    y = cy + radius * math.sin(angle_radians)
    return x, y

def get_time_info(gmt_offset_hours=0):
    """Devuelve los ángulos de las agujas y la fecha según zona horaria"""
    now_ts = time.time()
    utc_dt = datetime.fromtimestamp(now_ts, tz=timezone.utc)
    local_dt = utc_dt + timedelta(hours=gmt_offset_hours)

    h = local_dt.hour
    m = local_dt.minute
    s = local_dt.second + local_dt.microsecond / 1_000_000

    hour_angle = ((h % 12) + m / 60.0 + s / 3600.0) * 30.0
    minute_angle = (m + s / 60.0) * 6.0
    second_angle = s * 6.0

    # GMT/24h extra
    gmt_hour = local_dt.hour + local_dt.minute / 60.0
    gmt_angle = (gmt_hour / 24.0) * 360.0

    return {
        "hour_angle": hour_angle,
        "minute_angle": minute_angle,
        "second_angle": second_angle,
        "gmt_angle": gmt_angle,
        "date_text": str(local_dt.day),
        "time_str": local_dt.strftime("%H:%M:%S")
    }

# ----- Interfaz -----
class AnalogClock(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Reloj Rolex-like Multizona")
        self.resizable(False, False)

        # Variables seleccionables
        self.selected_style = tk.StringVar(value="Negro")
        self.selected_city = tk.StringVar(value="Bogotá")

        # Menús
        top_frame = tk.Frame(self, bg="black")
        top_frame.pack(fill="x")

        tk.Label(top_frame, text="Estilo:", fg="white", bg="black").pack(side="left", padx=5)
        tk.OptionMenu(top_frame, self.selected_style, *STYLES.keys(), command=self.change_style).pack(side="left")

        tk.Label(top_frame, text="Ciudad:", fg="white", bg="black").pack(side="left", padx=5)
        tk.OptionMenu(top_frame, self.selected_city, *WORLD_CITIES.keys(), command=self.change_city).pack(side="left")

        # Canvas principal
        self.canvas = tk.Canvas(self, width=WIDTH, height=HEIGHT, highlightthickness=0)
        self.canvas.pack()

        self.hand_ids = {}
        self.current_style = STYLES[self.selected_style.get()]
        self.gmt_offset = WORLD_CITIES[self.selected_city.get()]

        self._draw_background()
        self.update_clock()

    def change_style(self, *_):
        self.current_style = STYLES[self.selected_style.get()]
        self._draw_background()

    def change_city(self, *_):
        self.gmt_offset = WORLD_CITIES[self.selected_city.get()]

    def _draw_background(self):
        c = self.canvas
        c.delete("all")
        style = self.current_style

        c.configure(bg=style["bg"])

        # Dial
        c.create_oval(CENTER_X - RADIUS - 6, CENTER_Y - RADIUS - 6,
                      CENTER_X + RADIUS + 6, CENTER_Y + RADIUS + 6,
                      fill=style["dial"], outline="#222222")

        # Índices
        for minute in range(60):
            angle = minute * 6.0
            outer = RADIUS
            inner = RADIUS - (18 if minute % 5 == 0 else 8)
            width = 3 if minute % 5 == 0 else 1
            x1, y1 = polar_to_cart(CENTER_X, CENTER_Y, inner, angle)
            x2, y2 = polar_to_cart(CENTER_X, CENTER_Y, outer, angle)
            c.create_line(x1, y1, x2, y2, fill=style["marks"], width=width)

        # Marcadores especiales
        for h in range(12):
            angle = h * 30.0
            dot_r = 10
            pos = polar_to_cart(CENTER_X, CENTER_Y, RADIUS - 44, angle)
            if h == 0:
                tri_p1 = polar_to_cart(CENTER_X, CENTER_Y, RADIUS - 20, angle)
                tri_p2 = polar_to_cart(CENTER_X, CENTER_Y, RADIUS - 40, angle - 10)
                tri_p3 = polar_to_cart(CENTER_X, CENTER_Y, RADIUS - 40, angle + 10)
                c.create_polygon(tri_p1 + tri_p2 + tri_p3, fill=style["marks"], outline="")
            elif h in (3, 6, 9):
                x, y = pos
                c.create_rectangle(x-12, y-8, x+12, y+8, fill=style["marks"], outline="")
            else:
                x, y = pos
                c.create_oval(x - dot_r, y - dot_r, x + dot_r, y + dot_r, fill=style["marks"], outline="")

        # Texto
        c.create_text(CENTER_X, CENTER_Y - 60, text="ROLEX", font=("Helvetica", 22, "bold"), fill=style["marks"])
        c.create_text(CENTER_X, CENTER_Y - 34, text="OYSTER PERPETUAL DATE", font=("Helvetica", 9), fill=style["marks"])
        c.create_text(CENTER_X, CENTER_Y + 36, text="GMT-MASTER II", font=("Helvetica", 10, "bold"), fill=style["marks"])
        c.create_text(CENTER_X, CENTER_Y + 54, text="MULTIZONA CERTIFIED", font=("Helvetica", 8), fill=style["marks"])

        # Ventana de fecha
        date_w, date_h = 70, 48
        dx, dy = CENTER_X + RADIUS - 50, CENTER_Y - 10
        c.create_rectangle(dx - date_w//2, dy - date_h//2, dx + date_w//2, dy + date_h//2,
                           fill="#111111", outline="#666", width=2)
        c.create_rectangle(dx - date_w//2 + 4, dy - date_h//2 + 4,
                           dx + date_w//2 - 4, dy + date_h//2 - 4,
                           fill="#222222", outline="")
        c.create_oval(CENTER_X - 8, CENTER_Y - 8, CENTER_X + 8, CENTER_Y + 8,
                      fill="#111111", outline="#444")

    def update_clock(self):
        style = self.current_style
        info = get_time_info(self.gmt_offset)

        # Borrar agujas previas
        for ids in self.hand_ids.values():
            if isinstance(ids, list):
                for _id in ids: self.canvas.delete(_id)
            else:
                self.canvas.delete(ids)
        self.hand_ids.clear()

        # Hora
        hx, hy = polar_to_cart(CENTER_X, CENTER_Y, RADIUS * 0.52, info["hour_angle"])
        self.hand_ids["hour"] = self.canvas.create_line(CENTER_X, CENTER_Y, hx, hy,
                                                       width=8, capstyle=tk.ROUND, fill=style["hour"])
        # Minutos
        mx, my = polar_to_cart(CENTER_X, CENTER_Y, RADIUS * 0.78, info["minute_angle"])
        self.hand_ids["minute"] = self.canvas.create_line(CENTER_X, CENTER_Y, mx, my,
                                                         width=5, capstyle=tk.ROUND, fill=style["minute"])
        # Segundos
        sx, sy = polar_to_cart(CENTER_X, CENTER_Y, RADIUS * 0.88, info["second_angle"])
        line = self.canvas.create_line(CENTER_X, CENTER_Y, sx, sy,
                                       width=2, capstyle=tk.ROUND, fill=style["second"])
        dot = self.canvas.create_oval(sx-4, sy-4, sx+4, sy+4, fill=style["second"], outline="")
        self.hand_ids["second"] = [line, dot]

        # GMT
        gx, gy = polar_to_cart(CENTER_X, CENTER_Y, RADIUS * 0.62, info["gmt_angle"])
        gline = self.canvas.create_line(CENTER_X, CENTER_Y, gx, gy,
                                        width=3, dash=(3, 4), fill=style["gmt"])
        self.hand_ids["gmt"] = gline

        # Fecha
        dx, dy = CENTER_X + RADIUS - 50, CENTER_Y - 10
        self.hand_ids["date_text"] = self.canvas.create_text(dx, dy, text=info["date_text"],
                                                             font=("Helvetica", 20, "bold"), fill="black")

        # Texto ciudad y hora abajo
        city_text = f"{self.selected_city.get()}: {info['time_str']}"
        self.hand_ids["label"] = self.canvas.create_text(CENTER_X, HEIGHT - 20,
                                                         text=city_text, font=("Helvetica", 12),
                                                         fill=style["marks"])

        self.after(100, self.update_clock)


if __name__ == "__main__":
    app = AnalogClock()
    app.mainloop()



