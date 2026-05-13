import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkfont

# ------------------ Класс приложения ------------------
class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker - Трекер расходов")
        self.root.geometry("850x600")
        self.root.resizable(True, True)

        # Файл для хранения данных
        self.data_file = "expenses.json"

        # Загружаем данные
        self.expenses = self.load_expenses()

        # Настройка стилей
        self.setup_styles()

        # Создание интерфейса
        self.create_widgets()

        # Обновление таблицы и статистики
        self.refresh_table()
        self.update_stats()

    def setup_styles(self):
        """Настройка внешнего вида"""
        self.colors = {
            'bg': '#f0f0f0',
            'primary': '#2c3e50',
            'success': '#27ae60',
            'danger': '#e74c3c',
            'info': '#3498db'
        }
        self.root.configure(bg=self.colors['bg'])

        # Категории расходов
        self.categories = ['Еда', 'Транспорт', 'Развлечения',
                          'Жилье', 'Здоровье', 'Одежда',
                          'Образование', 'Другое']

    def create_widgets(self):
        """Создание всех элементов интерфейса"""
        # Основной контейнер с прокруткой
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # === Панель ввода ===
        input_frame = ttk.LabelFrame(main_frame, text="Добавить расход", padding=10)
        input_frame.pack(fill=tk.X, pady=(0, 10))

        # Поле Сумма
        ttk.Label(input_frame, text="Сумма (₽):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.amount_entry = ttk.Entry(input_frame, width=15)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)

        # Поле Категория
        ttk.Label(input_frame, text="Категория:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.category_var = tk.StringVar(value=self.categories[0])
        self.category_combo = ttk.Combobox(input_frame, textvariable=self.category_var,
                                           values=self.categories, width=15, state="readonly")
        self.category_combo.grid(row=0, column=3, padx=5, pady=5)

        # Поле Дата
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        self.date_entry = ttk.Entry(input_frame, width=12)
        self.date_entry.grid(row=0, column=5, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Кнопка Добавить
        self.add_btn = tk.Button(input_frame, text="+ Добавить расход",
                                 bg=self.colors['success'], fg='white',
                                 font=('Arial', 10, 'bold'),
                                 command=self.add_expense)
        self.add_btn.grid(row=0, column=6, padx=10, pady=5)

        # === Панель фильтрации ===
        filter_frame = ttk.LabelFrame(main_frame, text="Фильтрация", padding=10)
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        # Фильтр по категории
        ttk.Label(filter_frame, text="Категория:").grid(row=0, column=0, padx=5, pady=5)
        self.filter_category = ttk.Combobox(filter_frame, values=['Все'] + self.categories,
                                            width=15, state="readonly")
        self.filter_category.grid(row=0, column=1, padx=5, pady=5)
        self.filter_category.set('Все')

        # Фильтр по дате (период)
        ttk.Label(filter_frame, text="Дата от (ГГГГ-ММ-ДД):").grid(row=0, column=2, padx=5, pady=5)
        self.filter_date_from = ttk.Entry(filter_frame, width=12)
        self.filter_date_from.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(filter_frame, text="до:").grid(row=0, column=4, padx=5, pady=5)
        self.filter_date_to = ttk.Entry(filter_frame, width=12)
        self.filter_date_to.grid(row=0, column=5, padx=5, pady=5)

        # Кнопка Применить фильтр
        self.filter_btn = tk.Button(filter_frame, text="Применить фильтр",
                                    bg=self.colors['info'], fg='white',
                                    command=self.apply_filter)
        self.filter_btn.grid(row=0, column=6, padx=10, pady=5)

        # Кнопка Сбросить фильтр
        self.reset_btn = tk.Button(filter_frame, text="Сбросить",
                                   bg=self.colors['danger'], fg='white',
                                   command=self.reset_filter)
        self.reset_btn.grid(row=0, column=7, padx=5, pady=5)

        # === Таблица расходов ===
        table_frame = ttk.LabelFrame(main_frame, text="Список расходов", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Создание таблицы Treeview
        columns = ('id', 'amount', 'category', 'date')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)

        # Настройка колонок
        self.tree.heading('id', text='ID')
        self.tree.heading('amount', text='Сумма (₽)')
        self.tree.heading('category', text='Категория')
        self.tree.heading('date', text='Дата')

        self.tree.column('id', width=40, anchor=tk.CENTER)
        self.tree.column('amount', width=100, anchor=tk.CENTER)
        self.tree.column('category', width=120, anchor=tk.CENTER)
        self.tree.column('date', width=100, anchor=tk.CENTER)

        # Добавление скроллбара
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Контекстное меню для удаления
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Удалить запись", command=self.delete_selected)
        self.tree.bind("<Button-3>", self.show_context_menu)

        # === Панель статистики ===
        stats_frame = ttk.LabelFrame(main_frame, text="Статистика", padding=10)
        stats_frame.pack(fill=tk.X)

        self.stats_label = ttk.Label(stats_frame, text="", font=('Arial', 12, 'bold'))
        self.stats_label.pack()

    def load_expenses(self):
        """Загрузка расходов из JSON файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Добавляем ID, если нет
                    for i, exp in enumerate(data):
                        if 'id' not in exp:
                            exp['id'] = i + 1
                    return data
            except:
                return []
        return []

    def save_expenses(self):
        """Сохранение расходов в JSON файл"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.expenses, f, ensure_ascii=False, indent=2)

    def add_expense(self):
        """Добавление нового расхода"""
        # Валидация суммы
        amount_str = self.amount_entry.get().strip()
        if not amount_str:
            messagebox.showerror("Ошибка", "Введите сумму!")
            return

        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть положительным числом!")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Сумма должна быть числом!")
            return

        # Валидация даты
        date_str = self.date_entry.get().strip()
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")

        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ГГГГ-ММ-ДД")
            return

        # Создание записи
        new_id = max([exp['id'] for exp in self.expenses] + [0]) + 1
        expense = {
            'id': new_id,
            'amount': amount,
            'category': self.category_var.get(),
            'date': date_str
        }

        self.expenses.append(expense)
        self.save_expenses()

        # Очистка поля суммы
        self.amount_entry.delete(0, tk.END)

        # Обновление
        self.refresh_table()
        self.update_stats()
        messagebox.showinfo("Успех", f"Расход {amount} ₽ добавлен!")

    def delete_selected(self):
        """Удаление выбранной записи"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления!")
            return

        if messagebox.askyesno("Подтверждение", "Удалить выбранный расход?"):
            for item in selected:
                item_id = int(self.tree.item(item)['values'][0])
                self.expenses = [exp for exp in self.expenses if exp['id'] != item_id]

            # Перенумерация ID
            for i, exp in enumerate(self.expenses, 1):
                exp['id'] = i

            self.save_expenses()
            self.refresh_table()
            self.update_stats()
            messagebox.showinfo("Успех", "Запись удалена!")

    def show_context_menu(self, event):
        """Показать контекстное меню"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def get_filtered_expenses(self):
        """Получение отфильтрованных расходов"""
        filtered = self.expenses.copy()

        # Фильтр по категории
        cat_filter = self.filter_category.get()
        if cat_filter != 'Все':
            filtered = [exp for exp in filtered if exp['category'] == cat_filter]

        # Фильтр по дате (период)
        date_from = self.filter_date_from.get().strip()
        date_to = self.filter_date_to.get().strip()

        if date_from:
            try:
                from_date = datetime.strptime(date_from, "%Y-%m-%d")
                filtered = [exp for exp in filtered
                           if datetime.strptime(exp['date'], "%Y-%m-%d") >= from_date]
            except:
                pass

        if date_to:
            try:
                to_date = datetime.strptime(date_to, "%Y-%m-%d")
                filtered = [exp for exp in filtered
                           if datetime.strptime(exp['date'], "%Y-%m-%d") <= to_date]
            except:
                pass

        return filtered

    def refresh_table(self):
        """Обновление таблицы"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Добавление отфильтрованных записей
        for exp in self.get_filtered_expenses():
            self.tree.insert('', tk.END, values=(
                exp['id'],
                f"{exp['amount']:.2f}",
                exp['category'],
                exp['date']
            ))

    def update_stats(self):
        """Обновление статистики"""
        filtered = self.get_filtered_expenses()
        total = sum(exp['amount'] for exp in filtered)

        # Подсчет по категориям
        cat_stats = {}
        for exp in filtered:
            cat_stats[exp['category']] = cat_stats.get(exp['category'], 0) + exp['amount']

        stats_text = f"💰 Общая сумма за период: {total:.2f} ₽\n"
        if cat_stats:
            stats_text += "📊 По категориям: "
            stats_text += ", ".join([f"{cat}: {amt:.2f} ₽" for cat, amt in cat_stats.items()])

        self.stats_label.config(text=stats_text)

    def apply_filter(self):
        """Применение фильтров"""
        # Валидация дат, если введены
        date_from = self.filter_date_from.get().strip()
        date_to = self.filter_date_to.get().strip()

        if date_from:
            try:
                datetime.strptime(date_from, "%Y-%m-%d")
            except:
                messagebox.showerror("Ошибка", "Неверный формат даты 'от'! Используйте ГГГГ-ММ-ДД")
                return

        if date_to:
            try:
                datetime.strptime(date_to, "%Y-%m-%d")
            except:
                messagebox.showerror("Ошибка", "Неверный формат даты 'до'! Используйте ГГГГ-ММ-ДД")
                return

        self.refresh_table()
        self.update_stats()

    def reset_filter(self):
        """Сброс фильтров"""
        self.filter_category.set('Все')
        self.filter_date_from.delete(0, tk.END)
        self.filter_date_to.delete(0, tk.END)
        self.refresh_table()
        self.update_stats()


# ------------------ Запуск приложения ------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
