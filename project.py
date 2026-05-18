import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os

class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("800x600")

        # Загрузка избранного
        self.load_favorites()

        self.setup_ui()

    def setup_ui(self):
        # Поле поиска
        search_frame = ttk.Frame(self.root)
        search_frame.pack(pady=10, padx=20, fill="x")

        ttk.Label(search_frame, text="Поиск пользователя GitHub:").pack(side="left")

        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<Return>", lambda e: self.search_users())

        search_btn = ttk.Button(search_frame, text="Поиск", command=self.search_users)
        search_btn.pack(side="left", padx=5)

        # Результаты поиска
        results_frame = ttk.LabelFrame(self.root, text="Результаты поиска")
        results_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.results_listbox = tk.Listbox(results_frame, height=15)
        self.results_listbox.pack(fill="both", expand=True, padx=5, pady=5)

        add_favorite_btn = ttk.Button(results_frame, text="⭐ Добавить в избранное",
                                  command=self.add_to_favorites)
        add_favorite_btn.pack(pady=5)

        # Избранное
        favorites_frame = ttk.LabelFrame(self.root, text="Избранное")
        favorites_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.favorites_listbox = tk.Listbox(favorites_frame, height=8)
        self.favorites_listbox.pack(fill="both", expand=True, padx=5, pady=5)

        remove_favorite_btn = ttk.Button(favorites_frame, text="🗑️ Удалить из избранного",
                               command=self.remove_from_favorites)
        remove_favorite_btn.pack(pady=5)

    def search_users(self):
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showerror("Ошибка", "Поле поиска не должно быть пустым!")
            return

        try:
            response = requests.get(f"https://api.github.com/search/users?q={query}")
            response.raise_for_status()
            data = response.json()

            self.results_listbox.delete(0, tk.END)
            for user in data["items"][:10]:  # Ограничиваем 10 результатами
                self.results_listbox.insert(tk.END, f"{user['login']} (ID: {user['id']})")

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка", f"Ошибка при поиске: {e}")

    def load_favorites(self):
        if os.path.exists("favorites.json"):
            with open("favorites.json", "r", encoding="utf-8") as f:
                self.favorites = json.load(f)
        else:
            self.favorites = []
        self.update_favorites_display()

    def save_favorites(self):
        with open("favorites.json", "w", encoding="utf-8") as f:
            json.dump(self.favorites, f, ensure_ascii=False, indent=2)

    def update_favorites_display(self):
        self.favorites_listbox.delete(0, tk.END)
        for user in self.favorites:
            self.favorites_listbox.insert(tk.END, user["login"])

    def add_to_favorites(self):
        selection = self.results_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите пользователя из результатов поиска!")
            return

        selected_text = self.results_listbox.get(selection[0])
        login = selected_text.split(" (ID:")[0]

        if any(user["login"] == login for user in self.favorites):
            messagebox.showinfo("Информация", "Этот пользователь уже в избранном!")
            return

        # Получаем полную информацию о пользователе
        try:
            response = requests.get(f"https://api.github.com/users/{login}")
            response.raise_for_status()
            user_data = response.json()
            self.favorites.append(user_data)
            self.save_favorites()
            self.update_favorites_display()
            messagebox.showinfo("Успех", f"{login} добавлен в избранное!")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка", f"Не удалось получить данные пользователя: {e}")

    def remove_from_favorites(self):
        selection = self.favorites_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите пользователя из избранного!")
            return

        selected_login = self.favorites_listbox.get(selection[0])
        self.favorites = [user for user in self.favorites if user["login"] != selected_login]
        self.save_favorites()
        self.update_favorites_display()
        messagebox.showinfo("Успех", f"{selected_login} удалён из избранного!")

if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()

