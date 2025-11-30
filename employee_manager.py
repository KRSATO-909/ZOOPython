# employee_manager.py
import tkinter as tk
from tkinter import ttk, messagebox
import database

class EmployeeManager:
    def __init__(self, parent_window):
        self.window = tk.Toplevel(parent_window)
        self.window.title("Управление сотрудниками")
        self.window.geometry("700x450")

        self.first_name_var = tk.StringVar()
        self.last_name_var = tk.StringVar()
        self.position_var = tk.StringVar()

        self.current_id = None

        self.create_widgets()
        self.refresh_list()

    def create_widgets(self):
        # --- Форма ввода ---
        input_frame = tk.Frame(self.window)
        input_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        tk.Label(input_frame, text="Имя:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        tk.Entry(input_frame, textvariable=self.first_name_var).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)

        tk.Label(input_frame, text="Фамилия:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        tk.Entry(input_frame, textvariable=self.last_name_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)

        tk.Label(input_frame, text="Должность:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        tk.Entry(input_frame, textvariable=self.position_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=2)

        # --- Кнопки ---
        btn_frame = tk.Frame(input_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)

        self.add_btn = tk.Button(btn_frame, text="Добавить", command=self.add_employee)
        self.add_btn.pack(side=tk.LEFT, padx=5)

        self.edit_btn = tk.Button(btn_frame, text="Сохранить", command=self.update_employee, state=tk.DISABLED)
        self.edit_btn.pack(side=tk.LEFT, padx=5)

        self.cancel_btn = tk.Button(btn_frame, text="Отмена", command=self.cancel_edit, state=tk.DISABLED)
        self.cancel_btn.pack(side=tk.LEFT, padx=5)

        # --- Таблица ---
        list_frame = tk.Frame(self.window)
        list_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(list_frame, text="Список сотрудников:").pack(anchor=tk.W)

        columns = ("ID", "Имя", "Фамилия", "Должность")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120 if col != "ID" else 50)

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
        cursor.execute("SELECT id, first_name, last_name, position FROM employees ORDER BY last_name, first_name")
        for row in cursor.fetchall():
            self.tree.insert("", tk.END, values=row)
        conn.close()

    def add_employee(self):
        first = self.first_name_var.get().strip()
        last = self.last_name_var.get().strip()
        pos = self.position_var.get().strip()
        if not first or not last or not pos:
            messagebox.showwarning("Ошибка", "Все поля обязательны!")
            return
        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO employees (first_name, last_name, position) VALUES (?, ?, ?)",
                           (first, last, pos))
            conn.commit()
            conn.close()
            messagebox.showinfo("Успех", "Сотрудник добавлен!")
            self.clear_fields()
            self.refresh_list()
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка БД", str(e))

    def on_select(self, event):
        sel = self.tree.selection()
        if sel:
            values = self.tree.item(sel[0])["values"]
            self.first_name_var.set(values[1])
            self.last_name_var.set(values[2])
            self.position_var.set(values[3])
            self.current_id = values[0]
            self.add_btn.config(state=tk.DISABLED)
            self.edit_btn.config(state=tk.NORMAL)
            self.cancel_btn.config(state=tk.NORMAL)

    def update_employee(self):
        if not self.current_id:
            return
        first = self.first_name_var.get().strip()
        last = self.last_name_var.get().strip()
        pos = self.position_var.get().strip()
        if not first or not last or not pos:
            messagebox.showwarning("Ошибка", "Все поля обязательны!")
            return
        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE employees SET first_name=?, last_name=?, position=? WHERE id=?",
                           (first, last, pos, self.current_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Успех", "Данные сотрудника обновлены!")
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
        self.first_name_var.set("")
        self.last_name_var.set("")
        self.position_var.set("")

def open_employee_manager(parent):
    EmployeeManager(parent)