# seed_data.py
import sqlite3
from datetime import datetime, timedelta

DB_NAME = 'zoo.db'

def seed_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Вольеры
    enclosures = [
        ("Вольер №1", "Саванна", 5),
        ("Вольер №2", "Джунгли", 3),
        ("Вольер №3", "Пустыня", 2),
        ("Вольер №4", "Арктика", 4),
    ]
    cursor.executemany("INSERT OR IGNORE INTO enclosures (name, location, capacity) VALUES (?, ?, ?)", enclosures)

    # Сотрудники
    employees = [
        ("Иван", "Петров", "Смотритель"),
        ("Мария", "Сидорова", "Ветеринар"),
        ("Анна", "Кузнецова", "Смотритель"),
        ("Дмитрий", "Смирнов", "Администратор"),
    ]
    cursor.executemany("INSERT OR IGNORE INTO employees (first_name, last_name, position) VALUES (?, ?, ?)", employees)

    # Животные
    animals = [
        ("Лев", "Пантера львиная", "2018-03-15", "2020-01-10", 1, "Здоров"),
        ("Тигр", "Тигр амурский", "2019-07-22", "2021-05-14", 2, "На осмотре"),
        ("Верблюд", "Верблюд одногорбый", "2017-11-30", "2019-08-02", 3, "Здоров"),
        ("Пингвин", "Пингвин императорский", "2020-01-10", "2022-02-20", 4, "Лечится"),
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO animals (name, species, birth_date, arrival_date, enclosure_id, health_status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, animals)

    # Ветеринарные записи (привязка к ID животного)
    vet_records = [
        (1, "2024-11-01 10:00:00", "Мария Сидорова", "Профилактический осмотр", "Рекомендован витаминный комплекс"),
        (2, "2024-11-10 14:30:00", "Мария Сидорова", "Подозрение на ОРВИ", "Карантин на 3 дня"),
        (4, "2024-11-20 09:15:00", "Мария Сидорова", "Снижение аппетита", "Назначено лечение"),
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO veterinary_records (animal_id, date, veterinarian_name, diagnosis, treatment)
        VALUES (?, ?, ?, ?, ?)
    """, vet_records)

    # Учет кормления
    feeding = [
        (1, "Мясо", "2024-11-30 08:00:00", 2.5, 1),
        (2, "Мясо", "2024-11-30 08:15:00", 2.2, 3),
        (3, "Сено и вода", "2024-11-30 09:00:00", 5.0, 1),
        (4, "Рыба", "2024-11-30 07:30:00", 1.8, 3),
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO feeding_schedule (animal_id, feed_type, feed_time, amount, employee_id)
        VALUES (?, ?, ?, ?, ?)
    """, feeding)

    conn.commit()
    conn.close()
    print("✅ Тестовые данные успешно добавлены в базу данных!")

if __name__ == "__main__":
    seed_database()