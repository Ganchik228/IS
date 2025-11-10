#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Knight's Tour — Tkinter app
- Любой размер доски n x m
- Пользователь может указать старт кликом или через поля ввода
- Находит один полный тур (если он существует) или сообщает, что не найден
- Отображение результата статически (номера ходов) или анимацией перемещения фигуры
"""
import tkinter as tk
from tkinter import ttk, messagebox
import time
import random
import sys

# UI / визуальные настройки
CELL = 48
PADDING = 8
DEFAULT_N = 8
DEFAULT_M = 8
TIMEOUT_DEFAULT = 10.0  # сек — таймаут поиска решения

COLOR_WHITE = "#F8F8F8"
COLOR_BLACK = "#B4C7DC"
COLOR_CELL1 = "#f0d9b5"
COLOR_CELL2 = "#b58863"
COLOR_KNIGHT = "#1f77b4"
COLOR_TEXT = "black"
COLOR_HIGHLIGHT = "#ffeb3b"

MOVES = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]

class KnightTourApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Knight's Tour — Tkinter")
        self.resizable(False, False)

        self.n = DEFAULT_N
        self.m = DEFAULT_M
        self.start = (0, 0)
        self.board = None  # matrix for move indices (0 = unvisited)
        self.solution = None  # list of (r,c) moves if found
        self.animating = False
        self._after_id = None

        self._build_ui()
        self._create_board_model()

    def _build_ui(self):
        frm = ttk.Frame(self, padding=10)
        frm.grid(row=0, column=0)

        left = ttk.Frame(frm)
        left.grid(row=0, column=0, sticky="n")

        # Canvas for board
        self.canvas = tk.Canvas(left, width=self.m*CELL, height=self.n*CELL, bg="white")
        self.canvas.grid(row=0, column=0, columnspan=4)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # Controls
        controls = ttk.Frame(frm)
        controls.grid(row=0, column=1, padx=(12,0), sticky="n")

        ttk.Label(controls, text="Размер доски (n × m)").grid(row=0, column=0, columnspan=2, pady=(0,4))
        ttk.Label(controls, text="n (строки):").grid(row=1, column=0, sticky="e")
        self.var_n = tk.IntVar(value=self.n)
        ttk.Entry(controls, textvariable=self.var_n, width=6).grid(row=1, column=1, sticky="w")

        ttk.Label(controls, text="m (столбцы):").grid(row=2, column=0, sticky="e")
        self.var_m = tk.IntVar(value=self.m)
        ttk.Entry(controls, textvariable=self.var_m, width=6).grid(row=2, column=1, sticky="w")

        ttk.Separator(controls, orient="horizontal").grid(row=3, column=0, columnspan=2, sticky="ew", pady=6)

        ttk.Label(controls, text="Старт (0-indexed)").grid(row=4, column=0, columnspan=2)
        ttk.Label(controls, text="row:").grid(row=5, column=0, sticky="e")
        self.var_sr = tk.IntVar(value=self.start[0])
        ttk.Entry(controls, textvariable=self.var_sr, width=6).grid(row=5, column=1, sticky="w")
        ttk.Label(controls, text="col:").grid(row=6, column=0, sticky="e")
        self.var_sc = tk.IntVar(value=self.start[1])
        ttk.Entry(controls, textvariable=self.var_sc, width=6).grid(row=6, column=1, sticky="w")

        ttk.Separator(controls, orient="horizontal").grid(row=7, column=0, columnspan=2, sticky="ew", pady=6)

        ttk.Label(controls, text="Опции поиска:").grid(row=8, column=0, columnspan=2)
        ttk.Label(controls, text="Таймаут (сек):").grid(row=9, column=0, sticky="e")
        self.var_timeout = tk.DoubleVar(value=TIMEOUT_DEFAULT)
        ttk.Entry(controls, textvariable=self.var_timeout, width=6).grid(row=9, column=1, sticky="w")

        # Buttons
        btn_frame = ttk.Frame(controls)
        btn_frame.grid(row=10, column=0, columnspan=2, pady=8)
        ttk.Button(btn_frame, text="Применить размер", command=self.apply_size).grid(row=0, column=0, padx=4)
        ttk.Button(btn_frame, text="Очистить", command=self.reset_board).grid(row=0, column=1, padx=4)

        ttk.Button(controls, text="Найти решение", command=self.find_solution).grid(row=11, column=0, columnspan=2, sticky="ew", pady=(6,2))
        ttk.Button(controls, text="Показать статично", command=self.show_static).grid(row=12, column=0, columnspan=2, sticky="ew", pady=2)
        ttk.Button(controls, text="Анимировать", command=self.animate_solution).grid(row=13, column=0, columnspan=2, sticky="ew", pady=2)
        ttk.Button(controls, text="Остановить анимацию", command=self.stop_animation).grid(row=14, column=0, columnspan=2, sticky="ew", pady=2)

        ttk.Separator(controls, orient="horizontal").grid(row=15, column=0, columnspan=2, sticky="ew", pady=6)
        self.status = ttk.Label(controls, text="Кликните по клетке, чтобы задать старт (или введите координаты).")
        self.status.grid(row=16, column=0, columnspan=2)

        # Initial draw
        self._draw_board_canvas()

    def _create_board_model(self):
        self.board = [[0]*self.m for _ in range(self.n)]
        self.solution = None
        self._draw_board_canvas()

    def apply_size(self):
        n = self.var_n.get()
        m = self.var_m.get()
        if n <= 0 or m <= 0 or n > 40 or m > 40:
            messagebox.showwarning("Размер", "Допустимые значения n и m: 1..40 (рекомендация для удобства).")
            return
        self.n = n
        self.m = m
        # переприсвоить canvas размер
        self.canvas.config(width=self.m*CELL, height=self.n*CELL)
        self.start = (0, 0)
        self.var_sr.set(0)
        self.var_sc.set(0)
        self._create_board_model()

    def reset_board(self):
        self.start = (0, 0)
        self.var_sr.set(0)
        self.var_sc.set(0)
        self.solution = None
        self._create_board_model()
        self.status.config(text="Сброшено.")

    def on_canvas_click(self, ev):
        # выбрать клетку как старт
        c = ev.x // CELL
        r = ev.y // CELL
        if 0 <= r < self.n and 0 <= c < self.m:
            self.start = (r, c)
            self.var_sr.set(r)
            self.var_sc.set(c)
            self.solution = None
            self._draw_board_canvas()
            self.status.config(text=f"Старт установлен в ({r}, {c}).")

    def _draw_board_canvas(self, highlight=None, knight_pos=None, numbers=None):
        """
        highlight: set или список координат подсвечиваемых клеток
        knight_pos: (r,c) текущая позиция фигурки во время анимации
        numbers: dict {(r,c):num} для отображения номеров ходов
        """
        self.canvas.delete("all")
        for r in range(self.n):
            for c in range(self.m):
                x0 = c*CELL
                y0 = r*CELL
                x1 = x0 + CELL
                y1 = y0 + CELL
                color = COLOR_CELL1 if (r+c)%2==0 else COLOR_CELL2
                if highlight and (r,c) in highlight:
                    color = COLOR_HIGHLIGHT
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="gray")

                # номера ходов
                if numbers and (r,c) in numbers:
                    num = numbers[(r,c)]
                    self.canvas.create_text(x0 + CELL/2, y0 + CELL/2, text=str(num), fill=COLOR_TEXT, font=("Helvetica", 12, "bold"))

        # отмечаем старт
        sr, sc = self.start
        if 0 <= sr < self.n and 0 <= sc < self.m:
            cx = sc*CELL + CELL/2
            cy = sr*CELL + CELL/2
            r0 = CELL*0.22
            self.canvas.create_oval(cx-r0, cy-r0, cx+r0, cy+r0, fill="green", outline="black")
            self.canvas.create_text(cx, cy, text="S", fill="white", font=("Helvetica", 10, "bold"))

        # нарисовать коня, если задан
        if knight_pos:
            kr,kc = knight_pos
            cx = kc*CELL + CELL/2
            cy = kr*CELL + CELL/2
            r0 = CELL*0.26
            self.canvas.create_oval(cx-r0, cy-r0, cx+r0, cy+r0, fill=COLOR_KNIGHT, outline="black")
            self.canvas.create_text(cx, cy, text="♞", fill="white", font=("Helvetica", 14, "bold"))

        # подпись размеров
        self.update_idletasks()

    # --- Поиск решения (Warnsdorff + backtracking with timeout) ---
    def find_solution(self):
        # считываем входные данные
        try:
            sr = int(self.var_sr.get())
            sc = int(self.var_sc.get())
        except Exception:
            messagebox.showerror("Координаты", "Неверные координаты старта.")
            return
        if not (0 <= sr < self.n and 0 <= sc < self.m):
            messagebox.showerror("Координаты", "Старт находится вне доски.")
            return
        self.start = (sr, sc)
        self.solution = None
        total_cells = self.n * self.m
        timeout = float(self.var_timeout.get()) if self.var_timeout.get() > 0 else TIMEOUT_DEFAULT
        self.status.config(text=f"Поиск решения... (таймаут: {timeout:.1f}s). Подождите.")
        self.update()

        start_time = time.time()
        board = [[0]*self.m for _ in range(self.n)]
        path = []

        # Warnsdorff ordering helper
        def degree(r,c, b):
            cnt = 0
            for dr,dc in MOVES:
                nr, nc = r+dr, c+dc
                if 0 <= nr < self.n and 0 <= nc < self.m and b[nr][nc] == 0:
                    cnt += 1
            return cnt

        sys.setrecursionlimit(10000)

        found = False

        def dfs(r,c,step,b):
            nonlocal found, start_time
            # timeout check
            if time.time() - start_time > timeout:
                return False
            if found:
                return True
            b[r][c] = step
            path.append((r,c))
            if step == total_cells:
                found = True
                return True
            # generate neighbor list ordered by Warnsdorff (fewest onward moves)
            neigh = []
            for dr,dc in MOVES:
                nr, nc = r+dr, c+dc
                if 0 <= nr < self.n and 0 <= nc < self.m and b[nr][nc] == 0:
                    neigh.append((degree(nr,nc,b), nr, nc))
            neigh.sort(key=lambda x: x[0])
            # optional random tie-break to avoid same deterministic failure modes
            # group by degree and shuffle ties
            i = 0
            while i < len(neigh):
                j = i
                while j < len(neigh) and neigh[j][0] == neigh[i][0]:
                    j += 1
                if j - i > 1:
                    sub = neigh[i:j]
                    random.shuffle(sub)
                    neigh[i:j] = sub
                i = j
            for _, nr, nc in neigh:
                if dfs(nr, nc, step+1, b):
                    return True
            # backtrack
            b[r][c] = 0
            path.pop()
            return False

        ok = dfs(self.start[0], self.start[1], 1, board)
        if ok and found:
            # path holds the solution
            self.solution = list(path)  # copy
            self.status.config(text=f"Найдено решение: {len(self.solution)} ходов.")
            # показать статично по умолчанию
            self._show_numbers_on_board()
        else:
            self.solution = None
            if time.time() - start_time > timeout:
                self.status.config(text="Не найдено за отведённое время (таймаут).")
                messagebox.showinfo("Результат", "Решение не найдено за указанный таймаут.")
            else:
                self.status.config(text="Решение не найдено.")
                messagebox.showinfo("Результат", "Решение не существует (или не найдено).")

    def _show_numbers_on_board(self):
        if not self.solution:
            messagebox.showinfo("Нет решения", "Сначала найдите решение.")
            return
        nums = {}
        for i, (r,c) in enumerate(self.solution, start=1):
            nums[(r,c)] = i
        self._draw_board_canvas(numbers=nums)
        self.status.config(text="Показано статическое решение (номера ходов).")

    def show_static(self):
        if not self.solution:
            messagebox.showinfo("Нет решения", "Сначала найдите решение.")
            return
        self.stop_animation()
        self._show_numbers_on_board()

    def animate_solution(self):
        if not self.solution:
            messagebox.showinfo("Нет решения", "Сначала найдите решение.")
            return
        self.stop_animation()
        delay_ms = 250  # задержка между ходами (можно сделать параметром)
        self.animating = True
        self._animate_index = 0
        nums = {}
        for i, (r,c) in enumerate(self.solution, start=1):
            nums[(r,c)] = i
        # сначала отрисуем доску с номерами бледными (или без), но будем передвигать коня
        self._draw_board_canvas(numbers=None)
        def step():
            if not self.animating:
                return
            if self._animate_index >= len(self.solution):
                self.animating = False
                self.status.config(text="Анимация завершена.")
                return
            pos = self.solution[self._animate_index]
            # подсветить предыдущие шаги
            visited = set(self.solution[:self._animate_index+1])
            # отображаем номера для контекста
            nums2 = {}
            for i2, (rr,cc) in enumerate(self.solution[:self._animate_index+1], start=1):
                nums2[(rr,cc)] = i2
            self._draw_board_canvas(highlight=visited, knight_pos=pos, numbers=nums2)
            self._animate_index += 1
            self._after_id = self.after(delay_ms, step)
        self.status.config(text="Анимация запущена.")
        step()

    def stop_animation(self):
        self.animating = False
        if self._after_id:
            try:
                self.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None
        # после остановки перерисуем доску (если есть solution — покажем номера)
        if self.solution:
            self._show_numbers_on_board()
        else:
            self._draw_board_canvas()
        self.status.config(text="Анимация остановлена.")

if __name__ == "__main__":
    app = KnightTourApp()
    app.mainloop()
