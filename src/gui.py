"""Графический интерфейс для Password Manager"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from tkinter import font as tkfont
import os
import sys
import subprocess
import platform
from src.password_manager import PasswordManager
from src.password_generator import PasswordGenerator
from src.password_strength import PasswordStrengthAnalyzer


class PasswordManagerApp:
    """Главное окно приложения"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Password Manager")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)
        
        # Переменные
        self.manager = None
        self.current_vault = None
        
        # Цвета
        self.colors = {
            'bg': '#1e1e2e',
            'fg': '#cdd6f4',
            'accent': '#89b4fa',
            'success': '#a6e3a1',
            'danger': '#f38ba8',
            'warning': '#f9e2af'
        }
        
        # Настройка стиля
        self.setup_styles()
        
        # Создание интерфейса
        self.create_login_screen()
    
    def setup_styles(self):
        """Настройка стилей"""
        self.root.configure(bg=self.colors['bg'])
        
        # Настройка стиля для ttk
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('TFrame', background=self.colors['bg'])
        style.configure('TLabel', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('TButton', background=self.colors['accent'], foreground='black')
        style.configure('Title.TLabel', font=('Arial', 24, 'bold'), background=self.colors['bg'], foreground=self.colors['accent'])
        style.configure('Header.TLabel', font=('Arial', 14, 'bold'), background=self.colors['bg'], foreground=self.colors['fg'])
    
    def clear_window(self):
        """Очистка окна"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def create_login_screen(self):
        """Экран входа/регистрации"""
        self.clear_window()
        
        # Основной фрейм
        main_frame = ttk.Frame(self.root)
        main_frame.pack(expand=True, fill='both', padx=40, pady=40)
        
        # Заголовок
        ttk.Label(main_frame, text="🔐 Password Manager", style='Title.TLabel').pack(pady=(0, 30))
        
        # Подзаголовок
        ttk.Label(main_frame, text="Безопасное хранение ваших паролей", 
                  font=('Arial', 12), foreground=self.colors['fg']).pack(pady=(0, 30))
        
        # Форма входа
        login_frame = ttk.Frame(main_frame)
        login_frame.pack(pady=10)
        
        ttk.Label(login_frame, text="Путь к хранилищу (оставьте пустым для авто-определения):").grid(row=0, column=0, sticky='w', pady=5)
        self.vault_entry = ttk.Entry(login_frame, width=40)
        self.vault_entry.grid(row=0, column=1, pady=5, padx=10)
        self.vault_entry.insert(0, "")  # Пусто - будет авто-определение
        
        ttk.Label(login_frame, text="Мастер-пароль:").grid(row=1, column=0, sticky='w', pady=5)
        self.master_entry = ttk.Entry(login_frame, width=40, show="•")
        self.master_entry.grid(row=1, column=1, pady=5, padx=10)
        
        # Подсказка
        ttk.Label(login_frame, text="(оставьте поле пути пустым для автоматического поиска)", 
                  foreground=self.colors['warning'], font=('Arial', 8)).grid(row=2, column=0, columnspan=2, pady=5)
        
        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        def login():
            """Вход в хранилище"""
            try:
                # Если путь не указан - передаем None для авто-определения
                path = self.vault_entry.get().strip() or None
                self.manager = PasswordManager(
                    self.master_entry.get(),
                    path
                )
                self.current_vault = self.manager.storage.vault_path
                self.show_vault_screen()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось войти: {str(e)}")
        
        def create_new():
            """Создание нового хранилища"""
            try:
                master = self.master_entry.get()
                if len(master) < 8:
                    messagebox.showwarning("Ошибка", "Мастер-пароль должен быть минимум 8 символов!")
                    return
                
                path = self.vault_entry.get().strip() or None
                self.manager = PasswordManager(master, path)
                self.manager._save_vault()
                self.current_vault = self.manager.storage.vault_path
                messagebox.showinfo("Успех", f"✅ Хранилище создано!\nПуть: {self.current_vault}")
                self.show_vault_screen()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось создать хранилище: {str(e)}")
        
        ttk.Button(button_frame, text="🔑 Войти", command=login).pack(side='left', padx=5)
        ttk.Button(button_frame, text="🆕 Создать", command=create_new).pack(side='left', padx=5)
        
        # Статус
        self.status_label = ttk.Label(main_frame, text="", foreground=self.colors['warning'])
        self.status_label.pack(pady=10)
        
        # Привязка Enter
        self.master_entry.bind('<Return>', lambda e: login())
    
    def show_vault_screen(self):
        """Экран хранилища"""
        self.clear_window()
        
        # Главный фрейм
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Верхняя панель
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(top_frame, text="📂 Менеджер паролей", style='Header.TLabel').pack(side='left')
        
        # Информация
        info_text = f"Хранилище: {os.path.basename(self.current_vault)} | Записей: {len(self.manager.list_entries())}"
        ttk.Label(top_frame, text=info_text, foreground=self.colors['fg']).pack(side='right')
        
        # Панель поиска
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill='x', pady=10)
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=50)
        search_entry.pack(side='left', padx=(0, 10))
        search_entry.bind('<KeyRelease>', lambda e: self.refresh_entries())
        
        ttk.Button(search_frame, text="🔍 Поиск", command=self.refresh_entries).pack(side='left')
        
        # Кнопки действий
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill='x', pady=10)
        
        ttk.Button(action_frame, text="➕ Добавить", command=self.show_add_entry).pack(side='left', padx=2)
        ttk.Button(action_frame, text="🗑️ Удалить", command=self.delete_selected).pack(side='left', padx=2)
        ttk.Button(action_frame, text="💾 Экспорт", command=self.export_vault).pack(side='left', padx=2)
        ttk.Button(action_frame, text="🔑 Генератор", command=self.show_generator).pack(side='left', padx=2)
        ttk.Button(action_frame, text="📊 Проверить пароль", command=self.show_password_check).pack(side='left', padx=2)
        ttk.Button(action_frame, text="🚪 Выйти", command=self.create_login_screen).pack(side='right', padx=2)
        
        # Таблица записей
        self.create_entries_table(main_frame)
        
        # Статус
        self.status_label = ttk.Label(main_frame, text="Готово", foreground=self.colors['fg'])
        self.status_label.pack(pady=10)
        
        # Обновление списка
        self.refresh_entries()
    
    def create_entries_table(self, parent):
        """Создание таблицы записей"""
        # Фрейм для таблицы
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill='both', expand=True, pady=10)
        
        # Скроллбары
        scrollbar_y = ttk.Scrollbar(table_frame)
        scrollbar_y.pack(side='right', fill='y')
        
        scrollbar_x = ttk.Scrollbar(table_frame, orient='horizontal')
        scrollbar_x.pack(side='bottom', fill='x')
        
        # Таблица
        columns = ('login', 'url', 'password', 'created')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings',
                                 yscrollcommand=scrollbar_y.set,
                                 xscrollcommand=scrollbar_x.set)
        
        self.tree.heading('login', text='Логин')
        self.tree.heading('url', text='URL')
        self.tree.heading('password', text='Пароль')
        self.tree.heading('created', text='Создано')
        
        self.tree.column('login', width=200)
        self.tree.column('url', width=250)
        self.tree.column('password', width=150)
        self.tree.column('created', width=150)
        
        self.tree.pack(fill='both', expand=True)
        
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)
        
        # Двойной клик для просмотра
        self.tree.bind('<Double-Button-1>', self.show_entry_details)
    
    def refresh_entries(self):
        """Обновление списка записей"""
        if not self.manager:
            return
        
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Поиск
        query = self.search_var.get().strip()
        entries = self.manager.search_entries(query) if query else self.manager.list_entries()
        
        # Заполнение
        for entry in entries:
            self.tree.insert('', 'end', values=(
                entry.login,
                entry.url[:30] + '...' if len(entry.url) > 30 else entry.url,
                '*' * len(entry.password),
                entry.created_at[:10]
            ), tags=(entry.id,))
        
        # Обновление статуса
        self.status_label.config(text=f"Найдено: {len(entries)} записей")
    
    def show_add_entry(self):
        """Диалог добавления записи"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить запись")
        dialog.geometry("400x400")
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Форма
        frame = ttk.Frame(dialog)
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(frame, text="Логин:").grid(row=0, column=0, sticky='w', pady=5)
        login_entry = ttk.Entry(frame, width=40)
        login_entry.grid(row=0, column=1, pady=5, padx=10)
        
        ttk.Label(frame, text="Пароль:").grid(row=1, column=0, sticky='w', pady=5)
        password_entry = ttk.Entry(frame, width=40)
        password_entry.grid(row=1, column=1, pady=5, padx=10)
        
        def generate_password():
            """Генерация пароля"""
            gen = PasswordGenerator()
            password = gen.generate(length=16)
            password_entry.delete(0, tk.END)
            password_entry.insert(0, password)
        
        ttk.Button(frame, text="🔑 Сгенерировать", command=generate_password).grid(row=2, column=1, sticky='e', pady=5)
        
        ttk.Label(frame, text="URL:").grid(row=3, column=0, sticky='w', pady=5)
        url_entry = ttk.Entry(frame, width=40)
        url_entry.grid(row=3, column=1, pady=5, padx=10)
        
        ttk.Label(frame, text="Заметка:").grid(row=4, column=0, sticky='w', pady=5)
        note_text = scrolledtext.ScrolledText(frame, width=35, height=5)
        note_text.grid(row=4, column=1, pady=5, padx=10)
        
        def save():
            """Сохранение записи"""
            login = login_entry.get().strip()
            password = password_entry.get().strip()
            url = url_entry.get().strip()
            note = note_text.get('1.0', tk.END).strip()
            
            if not login or not password:
                messagebox.showwarning("Ошибка", "Логин и пароль обязательны!")
                return
            
            try:
                self.manager.add_entry(login, password, url, note)
                self.refresh_entries()
                dialog.destroy()
                messagebox.showinfo("Успех", "Запись добавлена!")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
        
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="💾 Сохранить", command=save).pack(side='left', padx=5)
        ttk.Button(button_frame, text="❌ Отмена", command=dialog.destroy).pack(side='left', padx=5)
    
    def show_entry_details(self, event):
        """Просмотр деталей записи"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        entry_id = self.tree.item(item)['tags'][0]
        entry = self.manager.get_entry(entry_id)
        
        if not entry:
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Запись: {entry.login}")
        dialog.geometry("500x400")
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog)
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        info = [
            ("Логин:", entry.login),
            ("Пароль:", entry.password),
            ("URL:", entry.url or "Нет"),
            ("Заметка:", entry.note or "Нет"),
            ("Создано:", entry.created_at),
            ("Обновлено:", entry.updated_at)
        ]
        
        for i, (label, value) in enumerate(info):
            ttk.Label(frame, text=label).grid(row=i, column=0, sticky='w', pady=5)
            ttk.Label(frame, text=value, foreground=self.colors['fg']).grid(row=i, column=1, sticky='w', pady=5, padx=10)
        
        def copy_password():
            """Копирование пароля в буфер"""
            self.root.clipboard_clear()
            self.root.clipboard_append(entry.password)
            messagebox.showinfo("Успех", "Пароль скопирован!")
        
        ttk.Button(frame, text="📋 Копировать пароль", command=copy_password).grid(row=6, column=0, columnspan=2, pady=20)
    
    def delete_selected(self):
        """Удаление выбранной записи"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Ошибка", "Выберите запись для удаления!")
            return
        
        if not messagebox.askyesno("Подтверждение", "Удалить выбранную запись?"):
            return
        
        item = selection[0]
        entry_id = self.tree.item(item)['tags'][0]
        
        if self.manager.delete_entry(entry_id):
            self.refresh_entries()
            messagebox.showinfo("Успех", "Запись удалена!")
    
    def export_vault(self):
        """Экспорт хранилища"""
        try:
            # Проверяем что есть записи
            if not self.manager or not self.manager.list_entries():
                messagebox.showwarning("Ошибка", "Нет записей для экспорта!")
                return
            
            # Открываем диалог выбора файла
            export_path = filedialog.asksaveasfilename(
                defaultextension=".vault",
                filetypes=[("Vault files", "*.vault"), ("All files", "*.*")],
                initialdir=os.path.expanduser("~"),
                title="Сохранить хранилище"
            )
            
            if export_path:
                try:
                    # Отладочный вывод
                    print(f"Экспорт в: {export_path}")
                    
                    # Экспортируем
                    self.manager.export_vault(export_path)
                    
                    # Сообщаем об успехе
                    messagebox.showinfo(
                        "Успех", 
                        f"✅ Хранилище экспортировано!\n\nПуть: {export_path}"
                    )
                    
                    # Дополнительно: запросить открыть папку
                    if messagebox.askyesno("Открыть папку", "Открыть папку с экспортированным файлом?"):
                        folder = os.path.dirname(export_path)
                        if platform.system() == 'Windows':
                            os.startfile(folder)
                        else:
                            subprocess.Popen(['explorer', folder])
                            
                except Exception as e:
                    messagebox.showerror(
                        "Ошибка", 
                        f"❌ Не удалось экспортировать:\n\n{str(e)}"
                    )
                    print(f"Ошибка экспорта: {e}")
                    import traceback
                    traceback.print_exc()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка: {str(e)}")
            print(f"Ошибка экспорта: {e}")
            import traceback
            traceback.print_exc()
    
    def show_generator(self):
        """Диалог генератора паролей"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Генератор паролей")
        dialog.geometry("400x300")
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog)
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(frame, text="Длина пароля:").pack(pady=5)
        length_var = tk.IntVar(value=16)
        length_scale = ttk.Scale(frame, from_=8, to=50, orient='horizontal', variable=length_var)
        length_scale.pack(fill='x', pady=5)
        length_label = ttk.Label(frame, text="16", foreground=self.colors['fg'])
        length_label.pack()
        
        def update_length(value):
            length_label.config(text=str(int(float(value))))
        length_scale.configure(command=update_length)
        
        result_label = ttk.Label(frame, text="", font=('Courier', 12), foreground=self.colors['accent'])
        result_label.pack(pady=20)
        
        def generate():
            gen = PasswordGenerator()
            password = gen.generate(length=length_var.get())
            result_label.config(text=password)
            
            # Проверка стойкости
            analyzer = PasswordStrengthAnalyzer()
            result = analyzer.classify_strength(password)
            strength_label.config(text=f"Стойкость: {result['strength']} (энтропия: {result['entropy']:.1f} бит)")
        
        ttk.Button(frame, text="🔑 Сгенерировать", command=generate).pack(pady=5)
        
        def copy_password():
            self.root.clipboard_clear()
            self.root.clipboard_append(result_label.cget('text'))
            messagebox.showinfo("Успех", "Пароль скопирован!")
        
        ttk.Button(frame, text="📋 Копировать", command=copy_password).pack(pady=5)
        
        strength_label = ttk.Label(frame, text="", foreground=self.colors['fg'])
        strength_label.pack(pady=10)
        
        generate()
    
    def show_password_check(self):
        """Диалог проверки пароля"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Проверка пароля")
        dialog.geometry("400x350")
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog)
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(frame, text="Введите пароль для проверки:").pack(pady=10)
        password_entry = ttk.Entry(frame, width=40, show="•")
        password_entry.pack(pady=10)
        
        result_text = scrolledtext.ScrolledText(frame, width=40, height=10)
        result_text.pack(pady=10)
        
        def check():
            password = password_entry.get()
            if not password:
                messagebox.showwarning("Ошибка", "Введите пароль!")
                return
            
            analyzer = PasswordStrengthAnalyzer()
            result = analyzer.classify_strength(password)
            
            result_text.delete('1.0', tk.END)
            result_text.insert('1.0', f"Результаты:\n")
            result_text.insert('end', f"{'─'*30}\n")
            result_text.insert('end', f"Длина: {result['length']} символов\n")
            result_text.insert('end', f"Энтропия: {result['entropy']} бит\n")
            result_text.insert('end', f"Стойкость: {result['strength']}\n")
            
            if result['warnings']:
                result_text.insert('end', f"\n⚠️ Предупреждения:\n")
                for warning in result['warnings']:
                    result_text.insert('end', f"• {warning}\n")
        
        ttk.Button(frame, text="📊 Проверить", command=check).pack(pady=10)


def main():
    """Запуск GUI приложения"""
    root = tk.Tk()
    app = PasswordManagerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()