import os
import csv

from dotenv import load_dotenv

import pandas as pd

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import numpy as np

load_dotenv()


def to_csv(user_id, exercise, amount):
    # * работа с csv
    exercises = {
        "user_id": user_id,
        "exercise": exercise,
        "amount": amount,
    }  # * словарь для записи упражнений для дальнейшего переноса в csv файл

    filename = os.getenv("CSV_URL")

    # * проверяем, нужно ли писать заголовки (если файл пустой/не существует)
    write_header = not os.path.exists(filename) or os.stat(filename).st_size == 0

    with open(filename, "a", newline="", encoding="utf-8") as csvfile:
        fieldnames = exercises.keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if write_header:
            writer.writeheader()  # * записываем загловки только если файл пустой
        writer.writerow(exercises)  # * записываем одну строку данных


def plot_exercises(
    csv_path=os.getenv("CSV_URL"),
    save_path=os.getenv("GRAPHICS_IMAGE_URL"),
    y_step=5,
    x_step=1,
):
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Ошибка: файл {csv_path} не найден")
        return

    # * создаем график
    plt.figure(figsize=(12, 6))

    # * для каждого уникального упражнения
    for exercise in df["exercise"].unique():
        # * фильтруем данные по упражнению
        subset = df[df["exercise"] == exercise]

        subset = subset.sort_index()

        # * добавляем начальную точку (1;0)
        x_values = [1] + subset.index.tolist()
        y_values = [0] + subset["amount"].tolist()

        plt.plot(
            x_values,
            y_values,
            marker="o",
            linestyle="-",
            linewidth=2,
            markersize=8,
            label=exercise,
        )

    # * настройки графика
    plt.title("Динамика выполнения упражнений", fontsize=14, pad=20)
    plt.xlabel("Номер тренировки", fontsize=12)
    plt.ylabel("Количество повторений", fontsize=12)

    max_amount = df["amount"].max()
    y_max = ((max_amount // y_step) + 1) * y_step
    plt.yticks(np.arange(0, y_max + 1, y_step))
    plt.xticks(np.arange(0, len(df) + 1, x_step))
    plt.grid(True, linestyle="--", alpha=0.7)

    plt.legend(
        title="Упражнения",
        bbox_to_anchor=(1.05, 1),
        loc="upper left",
        borderaxespad=0.0,
        fontsize=10,
    )

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
    else:
        plt.show()

    plt.close()
