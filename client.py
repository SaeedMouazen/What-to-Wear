import json
import socket
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

SERVER = "http://127.0.0.1:5050"

# The same city names as the CITIES dictionary in server.py.
CITIES = ["Riyadh", "Jeddah", "Madinah", "Abha", "Dammam"]


def send_request(path, values=None):
    """Send a request to Flask.
    Without values it is a GET. With values it is a POST.
    Returns (True, data) when it works, or (False, error message) when it fails."""
    body = None
    if values is not None:
        body = urlencode(values).encode("utf-8")
    try:
        with urlopen(SERVER + path, data=body, timeout=5) as reply:
            return True, json.loads(reply.read().decode("utf-8"))
    except HTTPError as error:
        # Flask answered with 400, 404, 500 or 503. Its JSON holds the message.
        data = json.loads(error.read().decode("utf-8"))
        return False, data["error"]
    except URLError:
        return False, "Can't reach the server. Make sure Flask is running, then try again."
    except socket.timeout:
        return False, "The server took too long to answer. Please try again."


class WardrobeWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("شلبس؟ What to Wear")
        self.option_add("*Font", ("Segoe UI", 11))
        self.selected_id = None
        self.selected_name = ""

        self.build_suggest_section()
        self.build_form_section()
        self.build_table_section()

        self.status_label = tk.Label(self, text="", anchor="w")
        self.status_label.grid(row=3, column=0, sticky="we", padx=10, pady=(0, 10))

        self.load_clothes()

    # ---------- building the window ----------

    def build_suggest_section(self):
        frame = tk.LabelFrame(self, text="شلبس؟  What should I wear?", padx=10, pady=10)
        frame.grid(row=0, column=0, sticky="we", padx=10, pady=10)

        tk.Label(frame, text="City").grid(row=0, column=0, sticky="w")
        self.city_box = ttk.Combobox(frame, values=CITIES, state="readonly", width=12)
        self.city_box.grid(row=0, column=1, sticky="w")
        self.city_box.set("Riyadh")

        tk.Label(frame, text="Going out at (hour 0-23)").grid(row=1, column=0, sticky="w")
        self.hour_box = tk.Spinbox(frame, from_=0, to=23, width=6)
        self.hour_box.grid(row=1, column=1, sticky="w")
        self.hour_box.delete(0, tk.END)
        self.hour_box.insert(0, str(datetime.now().hour))

        tk.Label(frame, text="Temperature (optional, °C)").grid(row=2, column=0, sticky="w")
        self.temp_box = tk.Entry(frame, width=8)
        self.temp_box.grid(row=2, column=1, sticky="w")
        tk.Label(frame, text="Leave it empty to use the forecast.", fg="gray").grid(row=3, column=0, columnspan=2, sticky="w")

        tk.Button(frame, text="شلبس؟", width=10, command=self.suggest).grid(row=0, column=2, rowspan=3, padx=15)

        self.result_label = tk.Label(frame, text="", justify="left", wraplength=420)
        self.result_label.grid(row=4, column=0, columnspan=3, sticky="w", pady=(8, 0))

    def build_form_section(self):
        frame = tk.LabelFrame(self, text="My Wardrobe", padx=10, pady=10)
        frame.grid(row=1, column=0, sticky="we", padx=10)

        tk.Label(frame, text="Name").grid(row=0, column=0, sticky="w")
        self.name_box = tk.Entry(frame, width=25)
        self.name_box.grid(row=0, column=1, columnspan=3, sticky="w")

        tk.Label(frame, text="Min temp (°C)").grid(row=1, column=0, sticky="w")
        self.min_box = tk.Entry(frame, width=8)
        self.min_box.grid(row=1, column=1, sticky="w")

        tk.Label(frame, text="Max temp (°C)").grid(row=1, column=2, sticky="w", padx=(10, 0))
        self.max_box = tk.Entry(frame, width=8)
        self.max_box.grid(row=1, column=3, sticky="w")

        buttons = tk.Frame(frame)
        buttons.grid(row=2, column=0, columnspan=4, sticky="w", pady=(10, 0))
        tk.Button(buttons, text="Save new", command=self.save_new).grid(row=0, column=0, padx=(0, 5))
        tk.Button(buttons, text="Update", command=self.update_selected).grid(row=0, column=1, padx=5)
        tk.Button(buttons, text="Delete", command=self.delete_selected).grid(row=0, column=2, padx=5)
        tk.Button(buttons, text="Clear", command=self.clear_form).grid(row=0, column=3, padx=5)
        tk.Button(buttons, text="Refresh", command=self.load_clothes).grid(row=0, column=4, padx=5)

    def build_table_section(self):
        columns = ("id", "name", "min_temp", "max_temp")
        self.table = ttk.Treeview(self, columns=columns, show="headings", height=8)
        self.table.heading("id", text="ID")
        self.table.heading("name", text="Name")
        self.table.heading("min_temp", text="Min °C")
        self.table.heading("max_temp", text="Max °C")
        self.table.column("id", width=50, anchor="center")
        self.table.column("name", width=220)
        self.table.column("min_temp", width=90, anchor="center")
        self.table.column("max_temp", width=90, anchor="center")
        self.table.grid(row=2, column=0, sticky="we", padx=10, pady=10)
        self.table.bind("<<TreeviewSelect>>", self.on_select)

    # ---------- small helpers ----------

    def show_status(self, text, is_error=False):
        if is_error:
            self.status_label.config(text=text, fg="red")
        else:
            self.status_label.config(text=text, fg="green")

    def read_form(self):
        return {
            "name": self.name_box.get(),
            "min_temp": self.min_box.get(),
            "max_temp": self.max_box.get(),
        }

    def clear_form(self):
        self.name_box.delete(0, tk.END)
        self.min_box.delete(0, tk.END)
        self.max_box.delete(0, tk.END)
        self.selected_id = None
        self.selected_name = ""
        self.table.selection_remove(self.table.selection())

    # ---------- actions ----------

    def load_clothes(self):
        ok, data = send_request("/clothes")
        if not ok:
            self.show_status(data, is_error=True)
            return
        for row in self.table.get_children():
            self.table.delete(row)
        for item in data:
            self.table.insert("", tk.END, values=(item["id"], item["name"], item["min_temp"], item["max_temp"]))
        if len(data) == 0:
            self.show_status("No clothes saved yet. Add your first item above.")
        else:
            self.show_status(f"{len(data)} items in your wardrobe.")

    def on_select(self, event):
        selection = self.table.selection()
        if not selection:
            return
        values = self.table.item(selection[0], "values")
        self.selected_id = values[0]
        self.selected_name = values[1]
        self.name_box.delete(0, tk.END)
        self.name_box.insert(0, values[1])
        self.min_box.delete(0, tk.END)
        self.min_box.insert(0, values[2])
        self.max_box.delete(0, tk.END)
        self.max_box.insert(0, values[3])

    def save_new(self):
        ok, data = send_request("/clothes/add", self.read_form())
        if not ok:
            self.show_status(data, is_error=True)
            return
        message = data["message"]
        self.clear_form()
        self.load_clothes()
        self.show_status(message)

    def update_selected(self):
        if self.selected_id is None:
            self.show_status("Select an item from the table first.", is_error=True)
            return
        ok, data = send_request(f"/clothes/{self.selected_id}/edit", self.read_form())
        if not ok:
            self.show_status(data, is_error=True)
            return
        message = data["message"]
        self.clear_form()
        self.load_clothes()
        self.show_status(message)

    def delete_selected(self):
        if self.selected_id is None:
            self.show_status("Select an item from the table first.", is_error=True)
            return
        if not messagebox.askyesno("Delete", f"Delete '{self.selected_name}'?"):
            return
        ok, data = send_request(f"/clothes/{self.selected_id}/delete", {})
        if not ok:
            self.show_status(data, is_error=True)
            return
        message = f"Deleted: {self.selected_name}"
        self.clear_form()
        self.load_clothes()
        self.show_status(message)

    def suggest(self):
        values = {
            "city": self.city_box.get(),
            "hour": self.hour_box.get(),
            "temp": self.temp_box.get(),
        }
        ok, data = send_request("/suggest?" + urlencode(values))
        if not ok:
            self.result_label.config(text=data, fg="red")
            return

        if data["source"] == "forecast":
            text = f"{data['city']} at {data['hour']}:00 feels like {data['feels_like']}°C."
        else:
            text = f"You typed {data['feels_like']}°C."

        names = []
        for item in data["clothes"]:
            names.append(item["name"])
        if len(names) == 0:
            text = text + " Nothing in your wardrobe fits. Add something for this temperature."
        else:
            text = text + " Wear: " + ", ".join(names)
        self.result_label.config(text=text, fg="black")


if __name__ == "__main__":
    window = WardrobeWindow()
    window.mainloop()