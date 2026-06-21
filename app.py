import json
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

DATA_FILE = "weather_data.json"


def load_records():
    try:
        with open(DATA_FILE, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_records(records):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def parse_date(s):
    try:
        return datetime.strptime(s.strip(), "%d.%m.%Y")
    except ValueError:
        return None


def parse_temp(s):
    try:
        return float(s.strip().replace(",", "."))
    except ValueError:
        return None


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Weather Diary")
        self.geometry("750x460")
        self.records = load_records()
        self._build()
        self._refresh()

    def _build(self):
        # --- ввод ---
        f = tk.LabelFrame(self, text="Новая запись", padx=6, pady=6)
        f.pack(fill="x", padx=8, pady=6)

        tk.Label(f, text="Дата (ДД.ММ.ГГГГ):").grid(row=0, column=0, sticky="w")
        self.e_date = tk.Entry(f, width=14)
        self.e_date.grid(row=0, column=1, padx=4)

        tk.Label(f, text="Температура:").grid(row=0, column=2, sticky="w")
        self.e_temp = tk.Entry(f, width=8)
        self.e_temp.grid(row=0, column=3, padx=4)

        tk.Label(f, text="Описание:").grid(row=0, column=4, sticky="w")
        self.e_desc = tk.Entry(f, width=22)
        self.e_desc.grid(row=0, column=5, padx=4)

        tk.Label(f, text="Осадки:").grid(row=0, column=6, sticky="w")
        self.v_precip = tk.StringVar(value="Нет")
        tk.OptionMenu(f, self.v_precip, "Нет", "Да").grid(row=0, column=7, padx=4)

        tk.Button(f, text="Добавить запись", command=self._add).grid(row=0, column=8, padx=6)

        # --- фильтр ---
        g = tk.LabelFrame(self, text="Фильтрация", padx=6, pady=6)
        g.pack(fill="x", padx=8)

        tk.Label(g, text="По дате:").grid(row=0, column=0, sticky="w")
        self.f_date = tk.Entry(g, width=12)
        self.f_date.grid(row=0, column=1, padx=4)

        tk.Label(g, text="Температура выше:").grid(row=0, column=2, sticky="w")
        self.f_temp = tk.Entry(g, width=8)
        self.f_temp.grid(row=0, column=3, padx=4)

        tk.Button(g, text="Применить", command=self._filter).grid(row=0, column=4, padx=6)
        tk.Button(g, text="Сброс", command=self._reset).grid(row=0, column=5)

        # --- таблица ---
        t = tk.Frame(self)
        t.pack(fill="both", expand=True, padx=8, pady=6)

        cols = ("date", "temp", "desc", "precip")
        self.tree = ttk.Treeview(t, columns=cols, show="headings")
        for col, head, w in [
            ("date", "Дата", 100), ("temp", "Температура", 100),
            ("desc", "Описание", 330), ("precip", "Осадки", 80),
        ]:
            self.tree.heading(col, text=head)
            self.tree.column(col, width=w)

        sb = ttk.Scrollbar(t, command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self.lbl_status = tk.Label(self, text="")
        self.lbl_status.pack(anchor="w", padx=8, pady=(0, 4))

    def _refresh(self, rows=None):
        self.tree.delete(*self.tree.get_children())
        for r in (rows if rows is not None else self.records):
            self.tree.insert("", "end", values=(r["date"], r["temp"], r["desc"], r["precip"]))
        n = len(rows) if rows is not None else len(self.records)
        self.lbl_status.config(text=f"Записей: {n}")

    def _add(self):
        date_s = self.e_date.get()
        temp_s = self.e_temp.get()
        desc   = self.e_desc.get()

        if not date_s.strip():
            messagebox.showerror("Ошибка", "Введите дату.")
            return
        if parse_date(date_s) is None:
            messagebox.showerror("Ошибка", "Неверный формат даты. Ожидается ДД.ММ.ГГГГ.")
            return
        if not temp_s.strip():
            messagebox.showerror("Ошибка", "Введите температуру.")
            return
        if parse_temp(temp_s) is None:
            messagebox.showerror("Ошибка", "Температура должна быть числом.")
            return
        if not desc.strip():
            messagebox.showerror("Ошибка", "Описание не должно быть пустым.")
            return

        record = {
            "date":   date_s.strip(),
            "temp":   parse_temp(temp_s),
            "desc":   desc.strip(),
            "precip": self.v_precip.get(),
        }
        self.records.append(record)
        save_records(self.records)
        self._refresh()
        self.e_date.delete(0, "end")
        self.e_temp.delete(0, "end")
        self.e_desc.delete(0, "end")
        self.v_precip.set("Нет")

    def _filter(self):
        date_f = self.f_date.get().strip()
        temp_f = self.f_temp.get().strip()
        result = list(self.records)

        if date_f:
            if parse_date(date_f) is None:
                messagebox.showerror("Ошибка", "Неверный формат даты для фильтра.")
                return
            result = [r for r in result if r["date"] == date_f]

        if temp_f:
            t = parse_temp(temp_f)
            if t is None:
                messagebox.showerror("Ошибка", "Порог температуры должен быть числом.")
                return
            result = [r for r in result if r["temp"] > t]

        self._refresh(result)

    def _reset(self):
        self.f_date.delete(0, "end")
        self.f_temp.delete(0, "end")
        self._refresh()


if __name__ == "__main__":
    App().mainloop()
