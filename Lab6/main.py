import tkinter as tk
from PIL import Image, ImageDraw
import numpy as np
import easyocr

reader = easyocr.Reader(['ru'], gpu=False)

root = tk.Tk()
root.title("Распознавание текста")
root.geometry("460x540")

main_frame = tk.Frame(root, padx=12, pady=12)
main_frame.pack(fill=tk.BOTH, expand=True)

tk.Label(main_frame, text="Размер кисти:", font=("Arial", 10)).pack(anchor=tk.W)
brush_size = tk.IntVar(value=5)
size_slider = tk.Scale(main_frame, from_=1, to=30, orient=tk.HORIZONTAL, variable=brush_size)
size_slider.pack(fill=tk.X)

def update_size_label(val=None):
    size_label.config(text=f"{brush_size.get()}px")

size_label = tk.Label(main_frame, text=f"{brush_size.get()} px", font=("Arial", 10))
size_label.pack(anchor=tk.W, pady=(0, 6))
size_slider.config(command=update_size_label)

canvas_label = tk.Label(main_frame, text="Нарисуйте текст:", font=("Arial", 10, "bold"))
canvas_label.pack(anchor=tk.W)

canvas_width = 400
canvas_height = 250
canvas = tk.Canvas(main_frame, width=canvas_width, height=canvas_height, bg="white", relief=tk.SOLID, bd=1)
canvas.pack(pady=(4, 8))

image = Image.new("RGB", (canvas_width, canvas_height), "white")
draw = ImageDraw.Draw(image)

def paint(event):
    size = brush_size.get()
    color = "black"
    
    x1, y1 = (event.x - size), (event.y - size)
    x2, y2 = (event.x + size), (event.y + size)
    
    canvas.create_oval(x1, y1, x2, y2, fill=color, outline=color)
    draw.ellipse([x1, y1, x2, y2], fill=color)

canvas.bind("<B1-Motion>", paint)

def clear():
    canvas.delete("all")
    draw.rectangle([0, 0, canvas_width, canvas_height], fill="white")
    result_label.config(text="")
    confidence_label.config(text="")
    status_label.config(text="Холст очищен")

def recognize():
    status_label.config(text="Распознавание...")
    root.update()
    
    img = np.array(image)
    
    result = reader.readtext(img)
    
    if result:
        text = " ".join([res[1] for res in result])
        avg_confidence = sum(res[2] for res in result) / len(result)
        confidence_label.config(text=f"Уверенность: {avg_confidence * 100:.1f}%")
    else:
        text = "Текст не обнаружен"
        confidence_label.config(text="Уверенность: 0.0%")
    
    result_label.config(text=text)
    status_label.config(text="Распознавание завершено")


buttons_frame = tk.Frame(main_frame)
buttons_frame.pack(fill=tk.X, pady=6)

btn_recognize = tk.Button(buttons_frame, text="Распознать", command=recognize, width=16)
btn_recognize.pack(side=tk.LEFT)

btn_clear = tk.Button(buttons_frame, text="Очистить", command=clear, width=16)
btn_clear.pack(side=tk.LEFT, padx=(8, 0))


status_label = tk.Label(main_frame, text="Готово")
status_label.pack(anchor=tk.W, pady=(0, 6))

result_frame = tk.LabelFrame(main_frame, text="Результат", padx=8, pady=8)
result_frame.pack(fill=tk.BOTH, expand=True)

result_label = tk.Label(result_frame, text="", font=("Arial", 12), wraplength=360, justify=tk.LEFT)
result_label.pack(fill=tk.X, anchor=tk.W)

confidence_label = tk.Label(result_frame, text="", font=("Arial", 11))
confidence_label.pack(fill=tk.X, anchor=tk.W, pady=(8, 0))

root.mainloop()