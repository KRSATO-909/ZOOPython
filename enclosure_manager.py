# enclosure_manager.py
import tkinter as tk
from tkinter import ttk, messagebox
import database

class EnclosureManager:
    def __init__(self, parent_window):
        self.window = tk.Toplevel(parent_window)
        self.window.title("Управление вольерами")
        self.window.geometry("700x450")

        self.name_var = tk.StringVar()
        self.location_var = tk.StringVar()
        self.capacity_var = tk.IntVar(value=1)

        self.current_id = None

        self.create_widgets()
        self.refresh_list()

    def create_widgets(self):
        # --- Форма ввода ---
        input_frame = tk.Frame(self.window)
        input_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        tk.Label(input_frame, text="Название:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        tk.Entry(input_frame, textvariable=self.name_var).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)

        tk.Label(input_frame, text="Местоположение:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        tk.Entry(input_frame, textvariable=self.location_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)

        tk.Label(input_frame, text="Вместимость:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        tk.Spinbox(input_frame, from_=1, to=100, textvariable=self.capacity_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=2)

        # --- Кнопки ---
        btn_frame = tk.Frame(input_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)

        self.add_btn = tk.Button(btn_frame, text="Добавить", command=self.add_enclosure)
        self.add_btn.pack(side=tk.LEFT, padx=5)

        self.edit_btn = tk.Button(btn_frame, text="Сохранить", command=self.update_enclosure, state=tk.DISABLED)
        self.edit_btn.pack(side=tk.LEFT, padx=5)

        self.cancel_btn = tk.Button(btn_frame, text="Отмена", command=self.cancel_edit, state=tk.DISABLED)
        self.cancel_btn.pack(side=tk.LEFT, padx=5)

        # --- Таблица ---
        list_frame = tk.Frame(self.window)
        list_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(list_frame, text="Список вольеров:").pack(anchor=tk.W)

        columns = ("ID", "Название", "Местоположение", "Вместимость")
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
        cursor.execute("SELECT id, name, location, capacity FROM enclosures ORDER BY name")
        for row in cursor.fetchall():
            self.tree.insert("", tk.END, values=row)
        conn.close()

    def add_enclosure(self):
        name = self.name_var.get().strip()
        location = self.location_var.get().strip()
        capacity = self.capacity_var.get()
        if not name or not location:
            messagebox.showwarning("Ошибка", "Название и местоположение обязательны!")
            return
        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO enclosures (name, location, capacity) VALUES (?, ?, ?)",
                           (name, location, capacity))
            conn.commit()
            conn.close()
            messagebox.showinfo("Успех", "Вольер добавлен!")
            self.clear_fields()
            self.refresh_list()
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка БД", str(e))

    def on_select(self, event):
        sel = self.tree.selection()
        if sel:
            values = self.tree.item(sel[0])["values"]
            self.name_var.set(values[1])
            self.location_var.set(values[2])
            self.capacity_var.set(values[3])
            self.current_id = values[0]
            self.add_btn.config(state=tk.DISABLED)
            self.edit_btn.config(state=tk.NORMAL)
            self.cancel_btn.config(state=tk.NORMAL)

    def update_enclosure(self):
        if not self.current_id:
            return
        name = self.name_var.get().strip()
        location = self.location_var.get().strip()
        capacity = self.capacity_var.get()
        if not name or not location:
            messagebox.showwarning("Ошибка", "Название и местоположение обязательны!")
            return
        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE enclosures SET name=?, location=?, capacity=? WHERE id=?",
                           (name, location, capacity, self.current_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Успех", "Данные вольера обновлены!")
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
        self.name_var.set("")
        self.location_var.set("")
        self.capacity_var.set(1)

def open_enclosure_manager(parent):
    EnclosureManager(parent)