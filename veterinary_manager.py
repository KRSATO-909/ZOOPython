# veterinary_manager.py
import tkinter as tk
from tkinter import ttk, messagebox
import database # Импортируем наш файл для работы с БД

class VeterinaryManager:
    def __init__(self, parent_window):
        # Создаем новое окно (Toplevel) для ветеринарного учета
        self.window = tk.Toplevel(parent_window)
        self.window.title("Ветеринарный учет")
        self.window.geometry("1000x600")

        # Переменные для хранения данных из полей ввода
        self.animal_id_var = tk.IntVar(value=0) # ID животного
        self.date_var = tk.StringVar() # Формат: YYYY-MM-DD HH:MM:SS
        self.vet_name_var = tk.StringVar()
        self.diagnosis_var = tk.StringVar()
        self.treatment_var = tk.StringVar()

        # Переменная для хранения ID редактируемой записи
        self.current_record_id = None

        # Создаем интерфейс
        self.create_widgets()

        # Загружаем список осмотров при открытии окна
        self.refresh_veterinary_list()

    def create_widgets(self):
        # --- Фрейм для ввода данных ---
        input_frame = tk.Frame(self.window)
        input_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        tk.Label(input_frame, text="ID Животного:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        tk.Entry(input_frame, textvariable=self.animal_id_var).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)

        tk.Label(input_frame, text="Дата осмотра (YYYY-MM-DD HH:MM:SS):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        tk.Entry(input_frame, textvariable=self.date_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)
        # Примечание: Для более удобного ввода даты можно использовать виджет Calendar, но для простоты оставим Entry

        tk.Label(input_frame, text="Имя ветеринара:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        tk.Entry(input_frame, textvariable=self.vet_name_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=2)

        tk.Label(input_frame, text="Диагноз:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        tk.Entry(input_frame, textvariable=self.diagnosis_var).grid(row=3, column=1, sticky=tk.EW, padx=5, pady=2)

        tk.Label(input_frame, text="Лечение:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        tk.Entry(input_frame, textvariable=self.treatment_var).grid(row=4, column=1, sticky=tk.EW, padx=5, pady=2)

        # --- Кнопки ---
        button_frame = tk.Frame(input_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)

        self.add_button = tk.Button(button_frame, text="Добавить осмотр", command=self.add_record)
        self.add_button.pack(side=tk.LEFT, padx=5)

        self.edit_button = tk.Button(button_frame, text="Сохранить изменения", command=self.update_record, state=tk.DISABLED)
        self.edit_button.pack(side=tk.LEFT, padx=5)

        self.cancel_button = tk.Button(button_frame, text="Отмена", command=self.cancel_edit, state=tk.DISABLED)
        self.cancel_button.pack(side=tk.LEFT, padx=5)

        # --- Фрейм для списка осмотров ---
        list_frame = tk.Frame(self.window)
        list_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(list_frame, text="История ветеринарных осмотров:").pack(anchor=tk.W)

        # Создаем Treeview (таблицу) для отображения осмотров
        # Включаем ID животного, чтобы пользователь мог понять, какому животному принадлежит осмотр
        columns = ("ID", "ID Животного", "Кличка Животного", "Дата", "Ветеринар", "Диагноз", "Лечение")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            # Устанавливаем ширину колонок
            if col == "Кличка Животного":
                self.tree.column(col, width=120)
            elif col == "Дата":
                self.tree.column(col, width=140)
            elif col == "Ветеринар":
                self.tree.column(col, width=120)
            elif col == "Диагноз" or col == "Лечение":
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

    def refresh_veterinary_list(self):
        # Очищаем текущий список в Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Получаем данные из БД
        conn = database.get_connection()
        cursor = conn.cursor()
        # JOIN с таблицей animals для отображения клички животного
        cursor.execute("""
            SELECT vr.id, vr.animal_id, a.name, vr.date, vr.veterinarian_name, vr.diagnosis, vr.treatment
            FROM veterinary_records vr
            LEFT JOIN animals a ON vr.animal_id = a.id
            ORDER BY vr.date DESC -- Сортировка по дате, новые первыми
        """)
        rows = cursor.fetchall()
        conn.close()

        # Заполняем Treeview
        for row in rows:
            # Если a.name = NULL (животное было удалено, но осмотр остался), отображаем ID
            animal_name = row[2] if row[2] else f"ID: {row[1]} (удалено)"
            display_row = (row[0], row[1], animal_name, row[3], row[4], row[5], row[6])
            self.tree.insert("", tk.END, values=display_row)

    def add_record(self):
        animal_id = self.animal_id_var.get()
        date = self.date_var.get().strip()
        vet_name = self.vet_name_var.get().strip()
        diagnosis = self.diagnosis_var.get().strip()
        treatment = self.treatment_var.get().strip()

        # Проверяем обязательные поля
        if not animal_id or not date or not vet_name:
            messagebox.showwarning("Предупреждение", "ID животного, дата и имя ветеринара обязательны для заполнения.")
            return

        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO veterinary_records (animal_id, date, veterinarian_name, diagnosis, treatment) VALUES (?, ?, ?, ?, ?)",
                (animal_id, date, vet_name, diagnosis, treatment)
            )
            conn.commit()
            conn.close()
            messagebox.showinfo("Успех", "Запись о ветеринарном осмотре добавлена!")
            self.clear_input_fields()
            self.refresh_veterinary_list()
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка БД", f"Ошибка при добавлении осмотра: {e}")

    def on_tree_select(self, event):
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            values = item["values"] # values = (ID, ID Животного, Кличка, Дата, Ветеринар, Диагноз, Лечение)
            # Заполняем поля ввода данными из выбранной строки
            # Примечание: Кличка (values[2]) не записывается обратно в поле ID животного
            self.animal_id_var.set(values[1]) # ID Животного
            self.date_var.set(values[3]) # Дата
            self.vet_name_var.set(values[4]) # Ветеринар
            self.diagnosis_var.set(values[5]) # Диагноз
            self.treatment_var.set(values[6]) # Лечение

            # Сохраняем ID выбранной записи для редактирования
            self.current_record_id = values[0]

            # Включаем кнопки редактирования и отмены
            self.add_button.config(state=tk.DISABLED)
            self.edit_button.config(state=tk.NORMAL)
            self.cancel_button.config(state=tk.NORMAL)

    def update_record(self):
        if self.current_record_id is None:
            messagebox.showwarning("Предупреждение", "Не выбрана запись для редактирования.")
            return

        animal_id = self.animal_id_var.get()
        date = self.date_var.get().strip()
        vet_name = self.vet_name_var.get().strip()
        diagnosis = self.diagnosis_var.get().strip()
        treatment = self.treatment_var.get().strip()

        # Проверяем обязательные поля
        if not animal_id or not date or not vet_name:
            messagebox.showwarning("Предупреждение", "ID животного, дата и имя ветеринара обязательны для заполнения.")
            return

        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE veterinary_records SET animal_id=?, date=?, veterinarian_name=?, diagnosis=?, treatment=?
                WHERE id=?""",
                (animal_id, date, vet_name, diagnosis, treatment, self.current_record_id)
            )
            conn.commit()
            conn.close()
            messagebox.showinfo("Успех", "Данные осмотра обновлены!")
            self.cancel_edit() # Сбрасываем форму
            self.refresh_veterinary_list()
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка БД", f"Ошибка при обновлении осмотра: {e}")

    def cancel_edit(self):
        # Сбрасываем ID редактируемой
        self.current_record_id = None
        # Очищаем поля ввода
        self.clear_input_fields()
        # Возвращаем кнопки в исходное состояние
        self.add_button.config(state=tk.NORMAL)
        self.edit_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.DISABLED)

    def clear_input_fields(self):
        self.animal_id_var.set(0)
        self.date_var.set("")
        self.vet_name_var.set("")
        self.diagnosis_var.set("")
        self.treatment_var.set("")


# --- Дополнительно: Функция для открытия окна (может быть вызвана из main.py) ---
def open_veterinary_manager(parent_window):
    VeterinaryManager(parent_window)