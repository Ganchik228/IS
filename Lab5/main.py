import random

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


def genetic_algorithm(target):
    population = [random_individual() for _ in range(POPULATION_SIZE)]

    for generation in range(1, GENERATIONS + 1):
        fitnesses = [fitness(ind, target) for ind in population]

        best_idx = min(range(POPULATION_SIZE), key=lambda i: fitnesses[i])
        best_fit = fitnesses[best_idx]

        if generation % 500 == 0 or best_fit == 0:
            total = sum(p * g for p, g in zip(PRICES, population[best_idx]))
            print(f"Поколение {generation:>5}: лучшая разница = {best_fit} руб. "
                  f"(сумма = {total} руб.)")

        if best_fit == 0:
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
    """Вывод выбранных сумок и итоговой суммы."""
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


def main():
    target = int(input("Введите целевую цену (руб.): "))
    print(f"\nЗапуск генетического алгоритма для целевой цены {target} руб.\n")

    best_individual, gen = genetic_algorithm(target)
    print_result(best_individual, target)
    print(f"Алгоритм завершился на поколении {gen}")


if __name__ == "__main__":
    main()
