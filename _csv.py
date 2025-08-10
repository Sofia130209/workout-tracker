import os, csv


def to_csv(user_id, exercise, amount):
    # * работа с csv
    exercises = {
        "user_id": user_id,
        "exercise": f"{exercise}",
        "amount": amount,
    }  # * словарь для записи упражнений для дальнейшего переноса в csv файл

    filename = "D:/PythonProjects/workouts_site/data/data.csv"

    # * проверяем, нужно ли писать заголовки (если файл пустой/не существует)
    write_header = not os.path.exists(filename) or os.stat(filename).st_size == 0

    with open(filename, "a", newline="") as csvfile:
        fieldnames = exercises.keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if write_header:
            writer.writeheader()  # * записываем загловки только если файл пустой
        writer.writerow(exercises)  # * записываем одну строку данных
