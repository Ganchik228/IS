import tkinter as tk
from tkinter import colorchooser
from PIL import Image, ImageDraw
import numpy as np
import easyocr

# Инициализация OCR
reader = easyocr.Reader(['en'], gpu=False)

# Создаем окно
root = tk.Tk()
root.title("Handwriting Recognition")
root.geometry("500x700")
root.configure(bg="#f0f0f0")

# Заголовок
title_frame = tk.Frame(root, bg="#2c3e50", height=60)
title_frame.pack(fill=tk.X)
title_label = tk.Label(title_frame, text="✏️ Handwriting Recognition", 
                       font=("Arial", 18, "bold"), bg="#2c3e50", fg="white", pady=10)
title_label.pack()

# Основной контейнер
main_frame = tk.Frame(root, bg="#f0f0f0")
main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

# Фрейм для настроек
settings_frame = tk.LabelFrame(main_frame, text="Настройки рисования", 
                               font=("Arial", 10, "bold"), bg="#f0f0f0", 
                               fg="#2c3e50", padx=10, pady=10)
settings_frame.pack(fill=tk.X, pady=(0, 10))

# Размер кисти
size_conf_frame = tk.Frame(settings_frame, bg="#f0f0f0")
size_conf_frame.pack(fill=tk.X, pady=5)

tk.Label(size_conf_frame, text="Размер кисти:", font=("Arial", 9), bg="#f0f0f0").pack(side=tk.LEFT)
brush_size = tk.IntVar(value=5)
size_slider = tk.Scale(size_conf_frame, from_=1, to=30, orient=tk.HORIZONTAL, 
                       variable=brush_size, bg="#ecf0f1", fg="#2c3e50", 
                       activebackground="#3498db", length=200)
size_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
size_label = tk.Label(size_conf_frame, text=f"{brush_size.get()}px", 
                      font=("Arial", 9, "bold"), bg="#f0f0f0", fg="#2c3e50", width=5)
size_label.pack(side=tk.LEFT)

def update_size_label(val=None):
    size_label.config(text=f"{brush_size.get()}px")

size_slider.config(command=update_size_label)

# Цвет кисти
color_frame = tk.Frame(settings_frame, bg="#f0f0f0")
color_frame.pack(fill=tk.X, pady=5)

tk.Label(color_frame, text="Цвет кисти:", font=("Arial", 9), bg="#f0f0f0").pack(side=tk.LEFT)

current_color = tk.StringVar(value="#000000")
color_display = tk.Label(color_frame, text="  ", bg=current_color.get(), 
                         width=3, relief=tk.SUNKEN, bd=2)
color_display.pack(side=tk.LEFT, padx=(10, 5))

def choose_color():
    color = colorchooser.askcolor(color=current_color.get())
    if color[1]:
        current_color.set(color[1])
        color_display.config(bg=current_color.get())

btn_color = tk.Button(color_frame, text="Выбрать цвет", command=choose_color,
                     bg="#3498db", fg="white", font=("Arial", 9), 
                     activebackground="#2980b9", padx=10)
btn_color.pack(side=tk.LEFT, padx=5)

# Холст
canvas_label = tk.Label(main_frame, text="Нарисуйте текст здесь:", 
                       font=("Arial", 10, "bold"), bg="#f0f0f0", fg="#2c3e50")
canvas_label.pack(anchor=tk.W, pady=(10, 5))

canvas_width = 400
canvas_height = 250
canvas = tk.Canvas(main_frame, width=canvas_width, height=canvas_height, 
                  bg="white", relief=tk.SUNKEN, bd=2, cursor="crosshair")
canvas.pack(pady=10)

# PIL изображение (для сохранения)
image = Image.new("RGB", (canvas_width, canvas_height), "white")
draw = ImageDraw.Draw(image)

# Рисование мышкой
def paint(event):
    size = brush_size.get()
    color = current_color.get()
    
    x1, y1 = (event.x - size), (event.y - size)
    x2, y2 = (event.x + size), (event.y + size)
    
    canvas.create_oval(x1, y1, x2, y2, fill=color, outline=color)
    draw.ellipse([x1, y1, x2, y2], fill=color)

canvas.bind("<B1-Motion>", paint)

# Очистка холста
def clear():
    canvas.delete("all")
    draw.rectangle([0, 0, canvas_width, canvas_height], fill="white")
    result_label.config(text="")
    status_label.config(text="Холст очищен")

# Распознавание
def recognize():
    status_label.config(text="Распознавание...", fg="#f39c12")
    root.update()
    
    # Конвертируем в numpy
    img = np.array(image)
    
    # easyocr
    result = reader.readtext(img)
    
    if result:
        text = " ".join([res[1] for res in result])
    else:
        text = "Текст не обнаружен"
    
    result_label.config(text=text)
    status_label.config(text="Распознавание завершено", fg="#27ae60")

# Кнопки
buttons_frame = tk.Frame(main_frame, bg="#f0f0f0")
buttons_frame.pack(fill=tk.X, pady=10)

btn_recognize = tk.Button(buttons_frame, text="🔍 Распознать", command=recognize,
                         bg="#27ae60", fg="white", font=("Arial", 11, "bold"),
                         activebackground="#229954", padx=15, pady=8, relief=tk.RAISED, bd=2)
btn_recognize.pack(side=tk.LEFT, padx=5)

btn_clear = tk.Button(buttons_frame, text="🗑️ Очистить", command=clear,
                     bg="#e74c3c", fg="white", font=("Arial", 11, "bold"),
                     activebackground="#c0392b", padx=15, pady=8, relief=tk.RAISED, bd=2)
btn_clear.pack(side=tk.LEFT, padx=5)

# Статус
status_label = tk.Label(main_frame, text="Готово к использованию", 
                       font=("Arial", 9), bg="#f0f0f0", fg="#7f8c8d")
status_label.pack(anchor=tk.W, pady=(5, 10))

# Результат
result_frame = tk.LabelFrame(main_frame, text="Результат распознавания", 
                            font=("Arial", 10, "bold"), bg="#f0f0f0",
                            fg="#2c3e50", padx=10, pady=10)
result_frame.pack(fill=tk.BOTH, expand=True, pady=10)

result_label = tk.Label(result_frame, text="", font=("Arial", 13, "bold"),
                       bg="#ecf0f1", fg="#2c3e50", wraplength=350, 
                       justify=tk.LEFT, relief=tk.SUNKEN, bd=1, padx=10, pady=10)
result_label.pack(fill=tk.BOTH, expand=True)

# Запуск
root.mainloop()