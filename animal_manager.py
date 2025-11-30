# animal_manager.py
import tkinter as tk
from tkinter import ttk, messagebox
import database # Импортируем наш файл для работы с БД

print('AnimalManager')
class AnimalManager:
    def __init__(self, parent_window):
        # Создаем новое окно (Toplevel) для управления животными
        self.window = tk.Toplevel(parent_window)
        self.window.title("Управление животными")
        self.window.geometry("900x500")

        # Переменные для хранения данных из полей ввода
        self.name_var = tk.StringVar()
        self.species_var = tk.StringVar()
        self.birth_date_var = tk.StringVar() # Формат: YYYY-MM-DD
        self.arrival_date_var = tk.StringVar() # Формат: YYYY-MM-DD
        self.enclosure_id_var = tk.IntVar(value=0) # По умолчанию 0, если не выбран
        self.health_status_var = tk.StringVar(value="Здоров")

        # Переменная для хранения ID редактируемого животного
        self.current_animal_id = None

        # Создаем интерфейс
        self.create_widgets()

        # Загружаем список животных при открытии окна
        self.refresh_animal_list()

    def create_widgets(self):
        # --- Фрейм для ввода данных ---
        input_frame = tk.Frame(self.window)
        input_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        tk.Label(input_frame, text="Кличка:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        tk.Entry(input_frame, textvariable=self.name_var).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)

        tk.Label(input_frame, text="Вид:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        tk.Entry(input_frame, textvariable=self.species_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)

        tk.Label(input_frame, text="Дата рождения (YYYY-MM-DD):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        tk.Entry(input_frame, textvariable=self.birth_date_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=2)

        tk.Label(input_frame, text="Дата поступления (YYYY-MM-DD):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        tk.Entry(input_frame, textvariable=self.arrival_date_var).grid(row=3, column=1, sticky=tk.EW, padx=5, pady=2)

        tk.Label(input_frame, text="ID Вольера:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        tk.Entry(input_frame, textvariable=self.enclosure_id_var).grid(row=4, column=1, sticky=tk.EW, padx=5, pady=2)

        tk.Label(input_frame, text="Состояние здоровья:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=2)
        health_options = ["Здоров", "На осмотре", "Лечится"]
        tk.OptionMenu(input_frame, self.health_status_var, *health_options).grid(row=5, column=1, sticky=tk.W, padx=5, pady=2)

        # --- Кнопки ---
        button_frame = tk.Frame(input_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)

        self.add_button = tk.Button(button_frame, text="Добавить", command=self.add_animal)
        self.add_button.pack(side=tk.LEFT, padx=5)

        self.edit_button = tk.Button(button_frame, text="Сохранить изменения", command=self.update_animal, state=tk.DISABLED)
        self.edit_button.pack(side=tk.LEFT, padx=5)

        self.cancel_button = tk.Button(button_frame, text="Отмена", command=self.cancel_edit, state=tk.DISABLED)
        self.cancel_button.pack(side=tk.LEFT, padx=5)

        # --- Фрейм для списка животных ---
        list_frame = tk.Frame(self.window)
        list_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(list_frame, text="Список животных:").pack(anchor=tk.W)

        # Создаем Treeview (таблицу) для отображения животных
        columns = ("ID", "Кличка", "Вид", "Дата рождения", "Дата поступления", "ID Вольера", "Состояние")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            # Устанавливаем ширину колонок
            if col == "Кличка" or col == "Вид":
                self.tree.column(col, width=100)
            elif col == "Дата рождения" or col == "Дата поступления":
                self.tree.column(col, width=100)
            else:
                self.tree.column(col, width=70)

        # Добавляем полосу прокрутки
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Привязываем событие клика к строке таблицы
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def refresh_animal_list(self):
        # Очищаем текущий список в Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Получаем данные из БД
        conn = database.get_connection()
        cursor = conn.cursor()
        # Запрашиваем все животные, можно добавить JOIN с enclosures для отображения имени вольера позже
        cursor.execute("SELECT id, name, species, birth_date, arrival_date, enclosure_id, health_status FROM animals ORDER BY name")
        rows = cursor.fetchall()
        conn.close()

        # Заполняем Treeview
        for row in rows:
            self.tree.insert("", tk.END, values=row)

    def add_animal(self):
        name = self.name_var.get().strip()
        species = self.species_var.get().strip()
        birth_date = self.birth_date_var.get().strip() # Проверку формата можно добавить позже
        arrival_date = self.arrival_date_var.get().strip()
        enclosure_id = self.enclosure_id_var.get()
        health_status = self.health_status_var.get()

        if not name or not species or not arrival_date:
            messagebox.showwarning("Предупреждение", "Кличка, вид и дата поступления обязательны для заполнения.")
            return

        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO animals (name, species, birth_date, arrival_date, enclosure_id, health_status) VALUES (?, ?, ?, ?, ?, ?)",
                (name, species, birth_date or None, arrival_date, enclosure_id or None, health_status)
            )
            conn.commit()
            conn.close()
            messagebox.showinfo("Успех", "Животное добавлено!")
            self.clear_input_fields()
            self.refresh_animal_list()
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка БД", f"Ошибка при добавлении животного: {e}")

    def on_tree_select(self, event):
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            values = item["values"]
            # Заполняем поля ввода данными из выбранной строки
            self.name_var.set(values[1])
            self.species_var.set(values[2])
            self.birth_date_var.set(values[3] if values[3] else "")
            self.arrival_date_var.set(values[4])
            self.enclosure_id_var.set(values[5] if values[5] else 0)
            self.health_status_var.set(values[6])

            # Сохраняем ID выбранного животного для редактирования
            self.current_animal_id = values[0]

            # Включаем кнопки редактирования и отмены
            self.add_button.config(state=tk.DISABLED)
            self.edit_button.config(state=tk.NORMAL)
            self.cancel_button.config(state=tk.NORMAL)

    def update_animal(self):
        if self.current_animal_id is None:
            messagebox.showwarning("Предупреждение", "Не выбрано животное для редактирования.")
            return

        name = self.name_var.get().strip()
        species = self.species_var.get().strip()
        birth_date = self.birth_date_var.get().strip()
        arrival_date = self.arrival_date_var.get().strip()
        enclosure_id = self.enclosure_id_var.get()
        health_status = self.health_status_var.get()

        if not name or not species or not arrival_date:
            messagebox.showwarning("Предупреждение", "Кличка, вид и дата поступления обязательны для заполнения.")
            return

        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE animals SET name=?, species=?, birth_date=?, arrival_date=?, enclosure_id=?, health_status=?
                WHERE id=?""",
                (name, species, birth_date or None, arrival_date, enclosure_id or None, health_status, self.current_animal_id)
            )
            conn.commit()
            conn.close()
            messagebox.showinfo("Успех", "Данные животного обновлены!")
            self.cancel_edit() # Сбрасываем форму
            self.refresh_animal_list()
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка БД", f"Ошибка при обновлении животного: {e}")

    def cancel_edit(self):
        # Сбрасываем ID редактируемого
        self.current_animal_id = None
        # Очищаем поля ввода
        self.clear_input_fields()
        # Возвращаем кнопки в исходное состояние
        self.add_button.config(state=tk.NORMAL)
        self.edit_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.DISABLED)

    def clear_input_fields(self):
        self.name_var.set("")
        self.species_var.set("")
        self.birth_date_var.set("")
        self.arrival_date_var.set("")
        self.enclosure_id_var.set(0)
        self.health_status_var.set("Здоров")


# --- Дополнительно: Функция для открытия окна (может быть вызвана из main.py) ---
def open_animal_manager(parent_window):
    AnimalManager(parent_window)