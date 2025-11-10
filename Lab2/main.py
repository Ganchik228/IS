import tkinter as tk
from tkinter import ttk, messagebox
import random
import sys

# Параметры по умолчанию
CELL_SIZE = 32
DEFAULT_ROWS = 8
DEFAULT_COLS = 10
MAX_CELLS = 12

# Цвета
COLOR_EMPTY = "white"
COLOR_WALL = "black"
COLOR_START = "green"
COLOR_END = "red"
COLOR_PATH = "yellow"
COLOR_VISITED = "#DDEEFF"

class MazeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Поиск маршрутов в лабиринте — Tkinter")
        self.rows = DEFAULT_ROWS
        self.cols = DEFAULT_COLS
        self.cell_size = CELL_SIZE

        # Модель лабиринта: 0 - пусто, 1 - стена
        self.grid = [[0]*self.cols for _ in range(self.rows)]
        self.start = (0, 0)
        self.end = (self.rows-1, self.cols-1)

        # Результаты поиска
        self.paths = []  # список путей (каждый путь — список координат)
        self.current_index = None

        self._build_ui()
        self._draw_grid()

    def _build_ui(self):
        # Левая часть: холст для рисования лабиринта
        left = ttk.Frame(self)
        left.grid(row=0, column=0, sticky="nswe", padx=6, pady=6)

        can_w = self.cols*self.cell_size
        can_h = self.rows*self.cell_size
        self.canvas = tk.Canvas(left, width=can_w, height=can_h, bg="white")
        self.canvas.grid(row=0, column=0, columnspan=4)
        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<B1-Motion>", self.on_left_drag)

        # Контролы
        ttk.Button(left, text="Очистить", command=self.clear_grid).grid(row=1, column=0, pady=6, sticky="ew")
        ttk.Button(left, text="Случайный", command=self.randomize).grid(row=1, column=1, pady=6, sticky="ew")
        ttk.Button(left, text="Решить", command=self.solve).grid(row=1, column=2, pady=6, sticky="ew")
        ttk.Button(left, text="Кратчайший", command=self.show_shortest).grid(row=1, column=3, pady=6, sticky="ew")

        ttk.Label(left, text="Строк:").grid(row=2, column=0, sticky="e")
        self.rows_var = tk.IntVar(value=self.rows)
        ttk.Entry(left, textvariable=self.rows_var, width=4).grid(row=2, column=1, sticky="w")
        ttk.Label(left, text="Столбцов:").grid(row=2, column=2, sticky="e")
        self.cols_var = tk.IntVar(value=self.cols)
        ttk.Entry(left, textvariable=self.cols_var, width=4).grid(row=2, column=3, sticky="w")
        ttk.Button(left, text="Применить размер", command=self.apply_size).grid(row=3, column=0, columnspan=4, sticky="ew", pady=6)

        # Правая часть: список путей и навигация
        right = ttk.Frame(self)
        right.grid(row=0, column=1, sticky="nswe", padx=6, pady=6)

        ttk.Label(right, text="Маршруты (длина)").grid(row=0, column=0)
        self.paths_list = tk.Listbox(right, width=30, height=20)
        self.paths_list.grid(row=1, column=0, sticky="nswe")
        self.paths_list.bind("<<ListboxSelect>>", self.on_list_select)

        nav = ttk.Frame(right)
        nav.grid(row=2, column=0, pady=6, sticky="ew")
        ttk.Button(nav, text="Предыдущий", command=self.show_prev).grid(row=0, column=0, padx=2)
        ttk.Button(nav, text="Следующий", command=self.show_next).grid(row=0, column=1, padx=2)
        ttk.Label(nav, text="Перейти к #:").grid(row=0, column=2, padx=(8,2))
        self.goto_var = tk.IntVar(value=1)
        ttk.Entry(nav, textvariable=self.goto_var, width=6).grid(row=0, column=3)
        ttk.Button(nav, text="Перейти", command=self.goto_index).grid(row=0, column=4, padx=2)

        info = ttk.Frame(right)
        info.grid(row=3, column=0, pady=6, sticky="ew")
        self.count_label = ttk.Label(info, text="Всего путей: 0")
        self.count_label.grid(row=0, column=0, sticky="w")
        self.current_label = ttk.Label(info, text="Текущий: -")
        self.current_label.grid(row=1, column=0, sticky="w")

        # Подсказки управления
        tips = ttk.Label(right, text=("ЛКМ: переключить стена/пусто. Перетащите ЛКМ для рисования.\n" 
                                      "ПКМ: установить старт/финиш по очереди (сначала старт, затем финиш)."))
        tips.grid(row=4, column=0, pady=6)

        # Конфигурация сетки (чтобы canvas ресайзился при изменении)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    # --- Взаимодействие с canvas ---
    def _draw_grid(self):
        self.canvas.delete('all')
        self.rects = [[None]*self.cols for _ in range(self.rows)]
        for r in range(self.rows):
            for c in range(self.cols):
                x0 = c*self.cell_size
                y0 = r*self.cell_size
                x1 = x0 + self.cell_size
                y1 = y0 + self.cell_size
                color = COLOR_EMPTY if self.grid[r][c] == 0 else COLOR_WALL
                rect = self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline='gray')
                self.rects[r][c] = rect
        # отрисовать старт/финиш поверх
        self._color_cell(self.start, COLOR_START)
        self._color_cell(self.end, COLOR_END)

    def _color_cell(self, pos, color, tag=None):
        r, c = pos
        if 0 <= r < self.rows and 0 <= c < self.cols:
            rect = self.rects[r][c]
            self.canvas.itemconfig(rect, fill=color)
            if tag:
                self.canvas.addtag_withtag(tag, rect)

    def on_left_click(self, event):
        r, c = self._pixel_to_cell(event.x, event.y)
        if r is None: return
        # переключаем стена/пусто, но не трогаем старт/финиш (если вершина совпадает)
        if (r,c) == self.start or (r,c) == self.end:
            return
        self.grid[r][c] = 0 if self.grid[r][c] == 1 else 1
        color = COLOR_EMPTY if self.grid[r][c] == 0 else COLOR_WALL
        self._color_cell((r,c), color)

    def on_left_drag(self, event):
        # при перетаскивании ставим стены
        r, c = self._pixel_to_cell(event.x, event.y)
        if r is None: return
        if (r,c) == self.start or (r,c) == self.end: return
        self.grid[r][c] = 1
        self._color_cell((r,c), COLOR_WALL)

    def on_right_click(self, event):
        r, c = self._pixel_to_cell(event.x, event.y)
        if r is None:
            return

        # если ни старт, ни финиш не заданы
        if self.start is None:
            self.start = (r, c)
        elif self.end is None:
            # если финиша нет, ставим финиш
            if (r, c) == self.start:
                return
            self.end = (r, c)
        else:
            # если оба есть, определяем куда попали кликом
            if (r, c) == self.start:
                # переместить старт
                self.start = (r, c)
            elif (r, c) == self.end:
                # переместить финиш
                self.end = (r, c)
            else:
                # если клик по пустой клетке — меняем ближайший
                dist_start = abs(r - self.start[0]) + abs(c - self.start[1])
                dist_end = abs(r - self.end[0]) + abs(c - self.end[1])
                if dist_start <= dist_end:
                    self.start = (r, c)
                else:
                    self.end = (r, c)

        # перерисовать сетку
        self._draw_grid()


    def _pixel_to_cell(self, x, y):
        c = x // self.cell_size
        r = y // self.cell_size
        if 0 <= r < self.rows and 0 <= c < self.cols:
            return r, c
        return None, None

    # --- Управление лабиринтом ---
    def clear_grid(self):
        for r in range(self.rows):
            for c in range(self.cols):
                self.grid[r][c] = 0
        self.start = (0,0)
        self.end = (self.rows-1, self.cols-1)
        self.paths = []
        self.current_index = None
        self._draw_grid()
        self._update_paths_ui()

    def randomize(self):
        for r in range(self.rows):
            for c in range(self.cols):
                self.grid[r][c] = 1 if random.random() < 0.3 else 0
        # ensure start/end not walls
        sr, sc = self.start
        er, ec = self.end
        self.grid[sr][sc] = 0
        self.grid[er][ec] = 0
        self.paths = []
        self.current_index = None
        self._draw_grid()
        self._update_paths_ui()

    def apply_size(self):
        r = self.rows_var.get()
        c = self.cols_var.get()
        if r <= 0 or c <= 0 or r > MAX_CELLS or c > MAX_CELLS:
            messagebox.showwarning("Размер", f"Допустимый размер: 1..{MAX_CELLS} для строк и столбцов (рекомендуется меньше для поиска всех путей)")
            return
        self.rows = r
        self.cols = c
        self.grid = [[0]*self.cols for _ in range(self.rows)]
        self.start = (0,0)
        self.end = (self.rows-1, self.cols-1)
        # ресайз canvas
        self.canvas.config(width=self.cols*self.cell_size, height=self.rows*self.cell_size)
        self.paths = []
        self.current_index = None
        self._draw_grid()
        self._update_paths_ui()

    # --- Поиск путей ---
    def solve(self):
        # Собираем все простые пути (без повторного посещения клеток) от start до end
        sr, sc = self.start
        er, ec = self.end
        if not (0 <= sr < self.rows and 0 <= sc < self.cols and 0 <= er < self.rows and 0 <= ec < self.cols):
            messagebox.showerror("Позиции", "Неправильно заданы старт/финиш")
            return
        if self.grid[sr][sc] == 1 or self.grid[er][ec] == 1:
            messagebox.showerror("Позиции", "Старт или финиш находятся в стене")
            return

        # Ограничение на размер (предупреждение)
        total_cells = self.rows * self.cols
        if total_cells > 100:
            if not messagebox.askyesno("Внимание", "Поиск всех путей на большой сетке может занять много времени. Продолжить?"):
                return

        # Выполняем DFS итеративно, собирая все пути.
        self.paths = []
        stack = [ ( (sr,sc), [(sr,sc)], set([(sr,sc)]) ) ]  # (pos, path_list, visited_set)
        while stack:
            pos, path, visited = stack.pop()
            if pos == (er,ec):
                self.paths.append(list(path))
                continue
            r,c = pos
            # соседи: вверх, вниз, влево, вправо
            for dr,dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                nr, nc = r+dr, c+dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    if self.grid[nr][nc] == 1: continue
                    if (nr,nc) in visited: continue
                    # отсечь пути, которые уже длиннее текущ известного кратчайшего (опция)
                    stack.append( ( (nr,nc), path+[(nr,nc)], visited | {(nr,nc)} ) )
        # После поиска — сортируем пути по длине
        self.paths.sort(key=lambda p: len(p))
        self.current_index = 0 if self.paths else None
        self._update_paths_ui()
        if self.current_index is not None:
            self._show_path(self.current_index)
        else:
            messagebox.showinfo("Результат", "Пути не найдены")

    def show_shortest(self):
        if not self.paths:
            messagebox.showinfo("Кратчайший", "Сначала выполните поиск (Решить)")
            return
        # Кратчайший — первый в отсортированном списке
        self.current_index = 0
        self._show_path(self.current_index)
        self.paths_list.selection_clear(0, tk.END)
        self.paths_list.selection_set(0)
        self.paths_list.see(0)

    def show_prev(self):
        if self.current_index is None:
            return
        if self.current_index > 0:
            self.current_index -= 1
            self._show_path(self.current_index)
            self.paths_list.selection_clear(0, tk.END)
            self.paths_list.selection_set(self.current_index)
            self.paths_list.see(self.current_index)

    def show_next(self):
        if self.current_index is None:
            return
        if self.current_index < len(self.paths)-1:
            self.current_index += 1
            self._show_path(self.current_index)
            self.paths_list.selection_clear(0, tk.END)
            self.paths_list.selection_set(self.current_index)
            self.paths_list.see(self.current_index)

    def goto_index(self):
        idx = self.goto_var.get() - 1
        if idx < 0 or idx >= len(self.paths):
            messagebox.showwarning("Номер", "Неверный номер маршрута")
            return
        self.current_index = idx
        self._show_path(self.current_index)
        self.paths_list.selection_clear(0, tk.END)
        self.paths_list.selection_set(self.current_index)
        self.paths_list.see(self.current_index)

    def on_list_select(self, event=None):
        sel = self.paths_list.curselection()
        if not sel: return
        idx = sel[0]
        self.current_index = idx
        self._show_path(idx)

    def _show_path(self, index):
        # Снять выделение предыдущих путей
        self._draw_grid()
        path = self.paths[index]
        # подсветить путь
        for (r,c) in path:
            self._color_cell((r,c), COLOR_PATH)
        # стилизовать старт/финиш
        self._color_cell(self.start, COLOR_START)
        self._color_cell(self.end, COLOR_END)
        self.current_label.config(text=f"Текущий: #{index+1} / {len(self.paths)}, длина {len(path)}")

    def _update_paths_ui(self):
        self.paths_list.delete(0, tk.END)
        for i,p in enumerate(self.paths):
            self.paths_list.insert(tk.END, f"#{i+1}: длина {len(p)}")
        self.count_label.config(text=f"Всего путей: {len(self.paths)}")
        if self.current_index is None:
            self.current_label.config(text="Текущий: -")
        
if __name__ == '__main__':
    app = MazeApp()
    app.mainloop()
