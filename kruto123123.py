import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime

DATA_FILE = 'expenses.json'

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.expenses = []

        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # Поля ввода
        ttk.Label(self.root, text="Сумма").grid(row=0, column=0, padx=5, pady=5)
        self.amount_entry = ttk.Entry(self.root)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.root, text="Категория").grid(row=0, column=2, padx=5, pady=5)
        self.category_var = tk.StringVar()
        self.category_combobox = ttk.Combobox(self.root, textvariable=self.category_var)
        self.category_combobox['values'] = ('Еда', 'Транспорт', 'Развлечения', 'Другое')
        self.category_combobox.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(self.root, text="Дата (YYYY-MM-DD)").grid(row=0, column=4, padx=5, pady=5)
        self.date_entry = ttk.Entry(self.root)
        self.date_entry.grid(row=0, column=5, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))

        # Добавление расхода
        add_button = ttk.Button(self.root, text="Добавить расход", command=self.add_expense)
        add_button.grid(row=0, column=6, padx=5, pady=5)

        # Таблица для отображения расходов
        columns = ('amount', 'category', 'date')
        self.tree = ttk.Treeview(self.root, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col.title())
        self.tree.grid(row=1, column=0, columnspan=7, padx=5, pady=5)

        # Фильтрация по категории
        ttk.Label(self.root, text="Фильтр по категории").grid(row=2, column=0, padx=5, pady=5)
        self.filter_category_var = tk.StringVar()
        self.filter_category_combobox = ttk.Combobox(self.root, textvariable=self.filter_category_var)
        self.filter_category_combobox['values'] = ('Все', 'Еда', 'Транспорт', 'Развлечения', 'Другое')
        self.filter_category_combobox.current(0)
        self.filter_category_combobox.grid(row=2, column=1, padx=5, pady=5)
        self.filter_category_combobox.bind("<<ComboboxSelected>>", self.apply_filters)

        # Фильтр по дате (по диапазону)
        ttk.Label(self.root, text="Дата от (YYYY-MM-DD)").grid(row=2, column=2, padx=5, pady=5)
        self.date_from_entry = ttk.Entry(self.root)
        self.date_from_entry.grid(row=2, column=3, padx=5, pady=5)

        ttk.Label(self.root, text="до").grid(row=2, column=4, padx=5, pady=5)
        self.date_to_entry = ttk.Entry(self.root)
        self.date_to_entry.grid(row=2, column=5, padx=5, pady=5)

        # Кнопка фильтрации и подсчёта
        filter_button = ttk.Button(self.root, text="Применить фильтры", command=self.apply_filters)
        filter_button.grid(row=2, column=6, padx=5, pady=5)

        # Итоговая сумма
        self.total_label = ttk.Label(self.root, text="Общая сумма: 0")
        self.total_label.grid(row=3, column=0, padx=5, pady=5)

    def load_data(self):
        try:
            with open(DATA_FILE, 'r') as f:
                self.expenses = json.load(f)
            for expense in self.expenses:
                self.insert_expense_in_table(expense)
        except (FileNotFoundError, json.JSONDecodeError):
            self.expenses = []

    def save_data(self):
        with open(DATA_FILE, 'w') as f:
            json.dump(self.expenses, f, ensure_ascii=False, indent=4)

    def add_expense(self):
        amount_text = self.amount_entry.get()
        category = self.category_var.get()
        date_text = self.date_entry.get()

        # Проверка
        try:
            amount = float(amount_text)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Введите положительное число для суммы")
            return

        try:
            # Проверка формата даты
            date_obj = datetime.strptime(date_text, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную дату в формате ГГГГ-ММ-ДД")
            return

        expense = {
            'amount': amount,
            'category': category,
            'date': date_text
        }
        self.expenses.append(expense)
        self.insert_expense_in_table(expense)
        self.save_data()

        # Очистка полей
        self.amount_entry.delete(0, tk.END)
        self.category_combobox.set('')
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))

        self.apply_filters()

    def insert_expense_in_table(self, expense):
        self.tree.insert('', tk.END, values=(expense['amount'], expense['category'], expense['date']))

    def apply_filters(self, event=None):
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Фильтруем
        filtered = []
        category_filter = self.filter_category_var.get()
        date_from_str = self.date_from_entry.get()
        date_to_str = self.date_to_entry.get()

        for exp in self.expenses:
            # Категория
            if category_filter != 'Все' and exp['category'] != category_filter:
                continue

            # Даты
            exp_date = datetime.strptime(exp['date'], '%Y-%m-%d')
            if date_from_str:
                try:
                    date_from = datetime.strptime(date_from_str, '%Y-%m-%d')
                    if exp_date < date_from:
                        continue
                except ValueError:
                    pass  # Игнорировать неверный формат
            if date_to_str:
                try:
                    date_to = datetime.strptime(date_to_str, '%Y-%m-%d')
                    if exp_date > date_to:
                        continue
                except ValueError:
                    pass

            filtered.append(exp)

        # отображаем отфильтрованные
        for exp in filtered:
            self.insert_expense_in_table(exp)

        # подсчет суммы
        total = sum(item['amount'] for item in filtered)
        self.total_label.config(text=f"Общая сумма: {total:.2f}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
