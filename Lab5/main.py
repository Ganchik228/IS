import random
import tkinter as tk
from tkinter import messagebox, ttk

BAGS = {
    "Сумка-1":  1,   "Сумка-2":  2,   "Сумка-3":  3,
    "Сумка-4":  4,   "Сумка-5":  5,   "Сумка-6":  6,
    "Сумка-7":  7,   "Сумка-8":  8,   "Сумка-9":  9,
    "Сумка-10": 10,  "Сумка-11": 15,  "Сумка-12": 20,
    "Сумка-13": 25,  "Сумка-14": 30,  "Сумка-15": 35,
    "Сумка-16": 40,  "Сумка-17": 45,  "Сумка-18": 50,
    "Сумка-19": 55,  "Сумка-20": 60,  "Сумка-21": 65,
    "Сумка-22": 70,  "Сумка-23": 75,  "Сумка-24": 80,
    "Сумка-25": 85,  "Сумка-26": 90,  "Сумка-27": 95,
    "Сумка-28": 100, "Сумка-29": 110, "Сумка-30": 120,
    "Сумка-31": 130, "Сумка-32": 140, "Сумка-33": 150,
    "Сумка-34": 160, "Сумка-35": 170, "Сумка-36": 180,
    "Сумка-37": 190, "Сумка-38": 200, "Сумка-39": 220,
    "Сумка-40": 240, "Сумка-41": 260, "Сумка-42": 280,
    "Сумка-43": 300, "Сумка-44": 350, "Сумка-45": 400,
    "Сумка-46": 450, "Сумка-47": 500, "Сумка-48": 600,
    "Сумка-49": 750, "Сумка-50": 900,
}

NAMES = list(BAGS.keys())
PRICES = list(BAGS.values())
N = len(PRICES)

POPULATION_SIZE = 200
GENERATIONS = 5000
CROSSOVER_RATE = 0.8
MUTATION_RATE = 0.05
ELITE_COUNT = 2


def random_individual():
    return [random.randint(0, 1) for _ in range(N)]


def fitness(individual, target):
    total = sum(p * g for p, g in zip(PRICES, individual))
    return abs(total - target)


def tournament_selection(population, fitnesses, k=3):
    candidates = random.sample(range(len(population)), k)
    best = min(candidates, key=lambda i: fitnesses[i])
    return population[best][:]


def crossover(parent1, parent2):
    if random.random() > CROSSOVER_RATE:
        return parent1[:], parent2[:]
    point = random.randint(1, N - 1)
    child1 = parent1[:point] + parent2[point:]
    child2 = parent2[:point] + parent1[point:]
    return child1, child2


def mutate(individual):
    for i in range(N):
        if random.random() < MUTATION_RATE:
            individual[i] = 1 - individual[i]


def genetic_algorithm(target, progress_callback=None):
    population = [random_individual() for _ in range(POPULATION_SIZE)]

    for generation in range(1, GENERATIONS + 1):
        fitnesses = [fitness(ind, target) for ind in population]

        best_idx = min(range(POPULATION_SIZE), key=lambda i: fitnesses[i])
        best_fit = fitnesses[best_idx]

        if generation % 500 == 0 or best_fit == 0:
            total = sum(p * g for p, g in zip(PRICES, population[best_idx]))
            message = (
                f"Поколение {generation:>5}: лучшая разница = {best_fit} руб. "
                f"(сумма = {total} руб.)"
            )
            if progress_callback:
                progress_callback(message)
            else:
                print(message)

        if best_fit == 0:
            if progress_callback:
                progress_callback(">>> Найдено точное совпадение!")
            else:
                print(">>> Найдено точное совпадение!")
            return population[best_idx], generation

        sorted_indices = sorted(range(POPULATION_SIZE), key=lambda i: fitnesses[i])
        new_population = [population[i][:] for i in sorted_indices[:ELITE_COUNT]]

        while len(new_population) < POPULATION_SIZE:
            p1 = tournament_selection(population, fitnesses)
            p2 = tournament_selection(population, fitnesses)
            c1, c2 = crossover(p1, p2)
            mutate(c1)
            mutate(c2)
            new_population.append(c1)
            if len(new_population) < POPULATION_SIZE:
                new_population.append(c2)

        population = new_population

    fitnesses = [fitness(ind, target) for ind in population]
    best_idx = min(range(POPULATION_SIZE), key=lambda i: fitnesses[i])
    return population[best_idx], GENERATIONS


def print_result(individual, target):
    selected = [(NAMES[i], PRICES[i]) for i in range(N) if individual[i] == 1]
    total = sum(price for _, price in selected)

    print("\n" + "=" * 55)
    print(f"Целевая цена:  {target} руб.")
    print(f"Набранная сумма: {total} руб.")
    print(f"Разница:        {abs(total - target)} руб.")
    print(f"Выбрано сумок:  {len(selected)}")
    print("-" * 55)
    for name, price in selected:
        print(f"  {name:<12} — {price:>5} руб.")
    print("=" * 55)


def build_result(individual, target):
    selected = [(NAMES[i], PRICES[i]) for i in range(N) if individual[i] == 1]
    total = sum(price for _, price in selected)
    diff = abs(total - target)
    return selected, total, diff


class GeneticApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Генетический алгоритм подбора сумок")
        self.root.geometry("900x650")
        self.root.minsize(760, 520)

        self.target_var = tk.StringVar()

        self.total_var = tk.StringVar(value="0 руб.")
        self.diff_var = tk.StringVar(value="0 руб.")
        self.count_var = tk.StringVar(value="0")
        self.gen_var = tk.StringVar(value="-")

        self._build_ui()

    def _build_ui(self):
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(fill=tk.X)

        ttk.Label(control_frame, text="Целевая цена (руб.):").pack(side=tk.LEFT)
        self.target_entry = ttk.Entry(control_frame, textvariable=self.target_var, width=16)
        self.target_entry.pack(side=tk.LEFT, padx=(8, 10))
        self.target_entry.focus_set()

        self.run_button = ttk.Button(control_frame, text="Запустить", command=self.run_algorithm)
        self.run_button.pack(side=tk.LEFT)

        self.root.bind("<Return>", lambda _: self.run_algorithm())

        summary = ttk.LabelFrame(self.root, text="Итог", padding=10)
        summary.pack(fill=tk.X, padx=10, pady=(0, 10))

        ttk.Label(summary, text="Набранная сумма:").grid(row=0, column=0, sticky="w", padx=(0, 8))
        ttk.Label(summary, textvariable=self.total_var).grid(row=0, column=1, sticky="w")

        ttk.Label(summary, text="Разница:").grid(row=0, column=2, sticky="w", padx=(20, 8))
        ttk.Label(summary, textvariable=self.diff_var).grid(row=0, column=3, sticky="w")

        ttk.Label(summary, text="Выбрано сумок:").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=(6, 0))
        ttk.Label(summary, textvariable=self.count_var).grid(row=1, column=1, sticky="w", pady=(6, 0))

        ttk.Label(summary, text="Поколение завершения:").grid(row=1, column=2, sticky="w", padx=(20, 8), pady=(6, 0))
        ttk.Label(summary, textvariable=self.gen_var).grid(row=1, column=3, sticky="w", pady=(6, 0))

        content = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        left_frame = ttk.LabelFrame(content, text="Выбранные сумки", padding=8)
        right_frame = ttk.LabelFrame(content, text="Все сумки", padding=8)
        content.add(left_frame, weight=2)
        content.add(right_frame, weight=3)

        self.tree = ttk.Treeview(left_frame, columns=("name", "price"), show="headings", height=16)
        self.tree.heading("name", text="Сумка")
        self.tree.heading("price", text="Цена (руб.)")
        self.tree.column("name", width=170, anchor="w")
        self.tree.column("price", width=110, anchor="e")

        tree_scroll = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.LEFT, fill=tk.Y)

        self.all_tree = ttk.Treeview(right_frame, columns=("name", "price", "selected"), show="headings", height=16)
        self.all_tree.heading("name", text="Сумка")
        self.all_tree.heading("price", text="Цена (руб.)")
        self.all_tree.heading("selected", text="Выбрана")
        self.all_tree.column("name", width=170, anchor="w")
        self.all_tree.column("price", width=110, anchor="e")
        self.all_tree.column("selected", width=90, anchor="center")

        all_tree_scroll = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.all_tree.yview)
        self.all_tree.configure(yscrollcommand=all_tree_scroll.set)

        self.all_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        all_tree_scroll.pack(side=tk.LEFT, fill=tk.Y)

        self._fill_all_bags_table()

    def append_log(self, message):
        self.root.update_idletasks()

    def clear_results(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        self._fill_all_bags_table()

        self.total_var.set("0 руб.")
        self.diff_var.set("0 руб.")
        self.count_var.set("0")
        self.gen_var.set("-")

    def _fill_all_bags_table(self, selected_indices=None):
        for item in self.all_tree.get_children():
            self.all_tree.delete(item)

        selected_indices = selected_indices or set()
        for i, (name, price) in enumerate(zip(NAMES, PRICES)):
            mark = "Да" if i in selected_indices else "Нет"
            self.all_tree.insert("", tk.END, values=(name, price, mark))

    def run_algorithm(self):
        raw_value = self.target_var.get().strip()
        if not raw_value:
            messagebox.showwarning("Ошибка ввода", "Введите целевую цену.")
            return

        try:
            target = int(raw_value)
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Целевая цена должна быть целым числом.")
            return

        if target < 0:
            messagebox.showerror("Ошибка ввода", "Целевая цена не может быть отрицательной.")
            return

        self.clear_results()
        self.run_button.configure(state=tk.DISABLED)

        try:
            best_individual, generation = genetic_algorithm(target, progress_callback=self.append_log)
            selected, total, diff = build_result(best_individual, target)

            for name, price in selected:
                self.tree.insert("", tk.END, values=(name, price))

            selected_indices = {i for i, g in enumerate(best_individual) if g == 1}
            self._fill_all_bags_table(selected_indices)

            self.total_var.set(f"{total} руб.")
            self.diff_var.set(f"{diff} руб.")
            self.count_var.set(str(len(selected)))
            self.gen_var.set(str(generation))
        finally:
            self.run_button.configure(state=tk.NORMAL)


def main():
    root = tk.Tk()
    app = GeneticApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
