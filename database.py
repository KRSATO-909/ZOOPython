# database.py
import sqlite3
import os

# Имя файла базы данных
DB_NAME = 'zoo.db'

def get_connection():
    """Возвращает соединение с базой данных."""
    conn = sqlite3.connect(DB_NAME)
    # Включаем поддержку внешних ключей (для SQLite это нужно включать явно)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_database():
    """Создает таблицы в базе данных, если их нет."""
    conn = get_connection()
    cursor = conn.cursor()

    # Создание таблицы вольеров
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS enclosures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            location TEXT NOT NULL,
            capacity INTEGER NOT NULL CHECK (capacity > 0)
        )
    ''')

    # Создание таблицы сотрудников
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            position TEXT NOT NULL
        )
    ''')

    # Создание таблицы животных
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS animals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            species TEXT NOT NULL,
            birth_date TEXT, -- Хранится как 'YYYY-MM-DD'
            arrival_date TEXT NOT NULL, -- Хранится как 'YYYY-MM-DD'
            enclosure_id INTEGER,
            health_status TEXT DEFAULT 'Здоров',
            FOREIGN KEY (enclosure_id) REFERENCES enclosures (id)
                ON DELETE SET NULL -- Если вольер удален, поле enclosure_id станет NULL
        )
    ''')

    # Создание таблицы ветеринарных осмотров
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS veterinary_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            animal_id INTEGER NOT NULL,
            date TEXT NOT NULL, -- 'YYYY-MM-DD HH:MM:SS'
            veterinarian_name TEXT NOT NULL,
            diagnosis TEXT,
            treatment TEXT,
            FOREIGN KEY (animal_id) REFERENCES animals (id)
                ON DELETE CASCADE -- Если животное удалено, его осмотры тоже удалятся
        )
    ''')

    # Создание таблицы кормления
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feeding_schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            animal_id INTEGER NOT NULL,
            feed_type TEXT NOT NULL,
            feed_time TEXT NOT NULL, -- 'YYYY-MM-DD HH:MM:SS'
            amount REAL NOT NULL CHECK (amount > 0),
            employee_id INTEGER, -- Кто кормил
            FOREIGN KEY (animal_id) REFERENCES animals (id)
                ON DELETE CASCADE,
            FOREIGN KEY (employee_id) REFERENCES employees (id)
                ON DELETE SET NULL
        )
    ''')

    conn.commit()
    conn.close()
    print(f"База данных '{DB_NAME}' и таблицы успешно инициализированы.")

if __name__ == "__main__":
    # Если запускаем этот файл напрямую, инициализируем БД
    init_database()