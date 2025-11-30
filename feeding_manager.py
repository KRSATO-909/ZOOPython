# feeding_manager.py
import tkinter as tk
from tkinter import ttk, messagebox
import database

class FeedingManager:
    def __init__(self, parent_window):
        self.window = tk.Toplevel(parent_window)
        self.window.title("Учет кормления")
        self.window.geometry("1000x550")

        self.animal_id_var = tk.IntVar(value=0)
        self.feed_type_var = tk.StringVar()
        self.feed_time_var = tk.StringVar()  # YYYY-MM-DD HH:MM:SS
        self.amount_var = tk.DoubleVar(value=0.0)
        self.employee_id_var = tk.IntVar(value=0)

        self.current_id = None

        self.create_widgets()
        self.refresh_list()

    def create_widgets(self):
        # --- Форма ввода ---
        input_frame = tk.Frame(self.window)
        input_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        tk.Label(input_frame, text="ID Животного:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        tk.Entry(input_frame, textvariable=self.animal_id_var).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)

        tk.Label(input_frame, text="Тип корма:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        tk.Entry(input_frame, textvariable=self.feed_type_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)

        tk.Label(input_frame, text="Время кормления (YYYY-MM-DD HH:MM:SS):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        tk.Entry(input_frame, textvariable=self.feed_time_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=2)

        tk.Label(input_frame, text="Количество (кг):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        tk.Entry(input_frame, textvariable=self.amount_var).grid(row=3, column=1, sticky=tk.EW, padx=5, pady=2)

        tk.Label(input_frame, text="ID Сотрудника:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        tk.Entry(input_frame, textvariable=self.employee_id_var).grid(row=4, column=1, sticky=tk.EW, padx=5, pady=2)

        # --- Кнопки ---
        btn_frame = tk.Frame(input_frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=10)

        self.add_btn = tk.Button(btn_frame, text="Добавить запись", command=self.add_feeding)
        self.add_btn.pack(side=tk.LEFT, padx=5)

        self.edit_btn = tk.Button(btn_frame, text="Сохранить", command=self.update_feeding, state=tk.DISABLED)
        self.edit_btn.pack(side=tk.LEFT, padx=5)

        self.cancel_btn = tk.Button(btn_frame, text="Отмена", command=self.cancel_edit, state=tk.DISABLED)
        self.cancel_btn.pack(side=tk.LEFT, padx=5)

        # --- Таблица ---
        list_frame = tk.Frame(self.window)
        list_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(list_frame, text="История кормлений:").pack(anchor=tk.W)

        columns = ("ID", "ID Животного", "Кличка", "Корм", "Время", "Кол-во (кг)", "ID Сотр.", "Сотрудник")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            if col == "Кличка" or col == "Сотрудник":
                self.tree.column(col, width=110)
            elif col == "Корм":
                self.tree.column(col, width=120)
            elif col == "Время":
                self.tree.column(col, width=140)
            else:
                self.tree.column(col, width=70)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                fs.id, 
                fs.animal_id, 
                a.name,
                fs.feed_type,
                fs.feed_time,
                fs.amount,
                fs.employee_id,
                e.last_name || ' ' || e.first_name
            FROM feeding_schedule fs
            LEFT JOIN animals a ON fs.animal_id = a.id
            LEFT JOIN employees e ON fs.employee_id = e.id
            ORDER BY fs.feed_time DESC
        """)
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            animal_name = row[2] if row[2] else f"ID: {row[1]} (удалено)"
            emp_name = row[7] if row[7] else f"ID: {row[6]}" if row[6] else ""
            self.tree.insert("", tk.END, values=(
                row[0], row[1], animal_name, row[3], row[4], row[5], row[6] or "", emp_name
            ))

    def add_feeding(self):
        animal_id = self.animal_id_var.get()
        feed_type = self.feed_type_var.get().strip()
        feed_time = self.feed_time_var.get().strip()
        amount = self.amount_var.get()
        employee_id = self.employee_id_var.get()

        if not animal_id or not feed_type or not feed_time or amount <= 0:
            messagebox.showwarning("Ошибка", "ID животного, тип корма, время и количество (>0) обязательны!")
            return

        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO feeding_schedule 
                (animal_id, feed_type, feed_time, amount, employee_id) 
                VALUES (?, ?, ?, ?, ?)
            """, (animal_id, feed_type, feed_time, amount, employee_id or None))
            conn.commit()
            conn.close()
            messagebox.showinfo("Успех", "Запись кормления добавлена!")
            self.clear_fields()
            self.refresh_list()
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка БД", str(e))

    def on_select(self, event):
        sel = self.tree.selection()
        if sel:
            values = self.tree.item(sel[0])["values"]
            self.animal_id_var.set(values[1])
            self.feed_type_var.set(values[3])
            self.feed_time_var.set(values[4])
            self.amount_var.set(float(values[5]))
            self.employee_id_var.set(values[6] if values[6] else 0)
            self.current_id = values[0]

            self.add_btn.config(state=tk.DISABLED)
            self.edit_btn.config(state=tk.NORMAL)
            self.cancel_btn.config(state=tk.NORMAL)

    def update_feeding(self):
        if not self.current_id:
            return
        animal_id = self.animal_id_var.get()
        feed_type = self.feed_type_var.get().strip()
        feed_time = self.feed_time_var.get().strip()
        amount = self.amount_var.get()
        employee_id = self.employee_id_var.get()

        if not animal_id or not feed_type or not feed_time or amount <= 0:
            messagebox.showwarning("Ошибка", "ID животного, тип корма, время и количество (>0) обязательны!")
            return

        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE feeding_schedule 
                SET animal_id=?, feed_type=?, feed_time=?, amount=?, employee_id=?
                WHERE id=?
            """, (animal_id, feed_type, feed_time, amount, employee_id or None, self.current_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Успех", "Данные кормления обновлены!")
            self.cancel_edit()
            self.refresh_list()
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка БД", str(e))

    def cancel_edit(self):
        self.current_id = None
        self.clear_fields()
        self.add_btn.config(state=tk.NORMAL)
        self.edit_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.DISABLED)

    def clear_fields(self):
        self.animal_id_var.set(0)
        self.feed_type_var.set("")
        self.feed_time_var.set("")
        self.amount_var.set(0.0)
        self.employee_id_var.set(0)

def open_feeding_manager(parent):
    FeedingManager(parent)