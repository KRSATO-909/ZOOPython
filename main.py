# main.py
import tkinter as tk
from tkinter import messagebox
import database
# Импортируем наши новые модули
import animal_manager
import veterinary_manager
import enclosure_manager
import employee_manager
import feeding_manager

class ZooApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Информационная Система Зоопарка")
        self.root.geometry("600x400")

        # Инициализируем базу данных при запуске
        database.init_database()

        # Создаем главное меню
        self.create_main_menu()

    def create_main_menu(self):
        """Создает главное меню приложения."""
        menu_frame = tk.Frame(self.root)
        menu_frame.pack(pady=50)

        title_label = tk.Label(menu_frame, text="Информационная Система Зоопарка", font=("Arial", 16))
        title_label.pack(pady=10)

        # Кнопки для основных модулей
        btn_animals = tk.Button(menu_frame, text="Управление животными", command=self.open_animal_window)
        btn_veterinary = tk.Button(menu_frame, text="Ветеринарный учет", command=self.open_veterinary_window)
        btn_feeding = tk.Button(menu_frame, text="Учет кормления", command=self.open_feeding_window)
        btn_employees = tk.Button(menu_frame, text="Управление сотрудниками", command=self.open_employee_window)
        btn_enclosures = tk.Button(menu_frame, text="Управление вольерами", command=self.open_enclosure_window)

        btn_animals.pack(fill=tk.X, padx=20, pady=5)
        btn_veterinary.pack(fill=tk.X, padx=20, pady=5)
        btn_feeding.pack(fill=tk.X, padx=20, pady=5)
        btn_employees.pack(fill=tk.X, padx=20, pady=5)
        btn_enclosures.pack(fill=tk.X, padx=20, pady=5)

    # Обновляем функцию
    def open_animal_window(self):
        animal_manager.open_animal_manager(self.root)

    # Обновляем функцию
    def open_veterinary_window(self):
        veterinary_manager.open_veterinary_manager(self.root)

    def open_feeding_window(self):
        feeding_manager.open_feeding_manager(self.root)
        
    def open_employee_window(self):
        employee_manager.open_employee_manager(self.root)
        
    def open_enclosure_window(self):
        enclosure_manager.open_enclosure_manager(self.root)

if __name__ == "__main__":
    root = tk.Tk()
    app = ZooApp(root)
    root.mainloop()