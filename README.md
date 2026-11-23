# What-to-Wear

Saeed Abdullah Muathin – 451000383
GitHub: https://github.com/SaeedMouazen/What-to-Wear

## What the app does

What to Wear helps you decide what to wear when you go out, which matters in November in Saudi Arabia, when noon can feel like summer and the evening like winter.

- You save your clothes, each with the temperature range it suits (for example: Jacket, -10°C to 17°C).
- You pick a **city** and the **hour** you are going out, then click **شلبس؟**.
- The app gets the forecast "feels like" temperature for that city and hour, and lists the clothes from your wardrobe that suit it.
- Without internet, you can type the temperature yourself instead.

The window (Tkinter) never touches the database. It sends HTTP requests to a Flask server, which checks the input, works with SQLite and replies with JSON:

```
client.py (Tkinter)  -- HTTP request -->  server.py (Flask)  -- SQL -->  wardrobe.db (SQLite)
                     <-- JSON reply ---          |
                                                 +-- HTTP --> Open-Meteo (weather forecast)
```

## Files

| File | What it does |
|---|---|
| `database.py` | `Database` class: creates the table and adds, reads, edits and deletes clothes. Run it once to create the table. |
| `server.py` | Flask server on port 5050: routes, input checks, weather forecast, JSON replies |
| `client.py` | Tkinter window: the only part the user works with |
| `report.py` | Report helper: writes the saved clothes to `wardrobe_report.txt` using a thread |
| `requirements.txt` | The Python packages to install (Flask) |

## Setup and running (Windows)

You need Python 3 installed. Run these commands in a terminal inside the project folder.

**1. Create a virtual environment and install the packages**
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
If `activate` says "running scripts is disabled", run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, then try again.

**2. Create the table**
```
python database.py
```
This creates `wardrobe.db` with 3 sample clothes. If the table already exists, the saved clothes are kept.

**3. Start Flask (terminal 1, leave it running)**
```
python server.py
```

**4. Start the window (terminal 2)**
```
venv\Scripts\activate
python client.py
```
Always start Flask first.

**5. Create the report (with Flask running)**
```
python report.py
```
The report is saved as `wardrobe_report.txt` in the project folder.

The forecast needs an internet connection. Without one, type the temperature in the window instead.

## Flask routes

| Method | Route | What it does | Replies |
|---|---|---|---|
| GET | `/clothes` | All saved clothes (also used by the report helper) | 200 |
| POST | `/clothes/add` | Checks and saves a new item | 201, or 400 for invalid input |
| POST | `/clothes/<id>/edit` | Checks and updates one item | 200, 400, or 404 for an unknown ID |
| POST | `/clothes/<id>/delete` | Deletes one item | 200, or 404 for an unknown ID |
| GET | `/suggest?city=&hour=&temp=` | Feels-like temperature and matching clothes | 200, 400, or 503 if the forecast is unavailable |

## Where each course topic appears

| Topic | Where in my project |
|---|---|
| Python and collections | **Lists:** `Database.get_all()` and `Database.get_for_temperature()` in `database.py` build a list of clothes; `CITIES` list in `client.py`. **Dictionaries:** `Database.row_to_dict()` turns each row into a dictionary; `CITIES` dictionary (city → location) in `server.py`; `read_form()` in `client.py`. **Loops and conditions:** `for` loops in `get_all()`, `WardrobeWindow.load_clothes()` and `WardrobeWindow.suggest()`; conditions in `check_number()` in `server.py`. |
| Exceptions | `server.py`: `check_number()` and `read_clothing_form()` raise `ValueError` for invalid input, and the routes catch it and reply 400; `suggest()` catches `URLError` and `socket.timeout` from the weather service; `@app.errorhandler(sqlite3.Error)` handles database errors. `database.py`: `try/finally` always closes the connection. `client.py`: `send_request()` catches `HTTPError`, `URLError` and `socket.timeout`. `report.py`: `write_report()` catches `OSError`. |
| Classes | `Database` class in `database.py` holds all database operations. `WardrobeWindow(tk.Tk)` in `client.py` is the window. |
| SQLite | `Database` in `database.py`: `create_table()` (`CREATE TABLE IF NOT EXISTS` keeps saved records), `add()`, `get_all()`, `get_for_temperature()`, `update()`, `delete()`. Every query uses `?` placeholders. Each method opens its own connection, commits changes and closes it. |
| Threads and files | `report.py`: `main()` creates one `threading.Thread`, calls `start()` and waits with `join()`; `write_report()` writes a UTF-8 text file using `with open(...)` and handles `OSError`. |
| Tkinter | `WardrobeWindow` in `client.py`: labels, text boxes, a city dropdown, an hour spinbox, buttons, a `Treeview` table, a delete confirmation (`messagebox.askyesno`) and a green/red status line (`show_status()`). |
| Client and server | `send_request()` in `client.py` sends every request with `urlopen`. See the example below. |
| Flask | `server.py`: routes `list_clothes()`, `add_clothing()`, `edit_clothing()`, `delete_clothing()` and `suggest()`; input checks in `check_number()` and `read_clothing_form()`; JSON replies with `jsonify()`. |

## One HTTP request and its reply

When the user types `Red shemagh`, `-10`, `20` and clicks **Save new**:

1. `WardrobeWindow.save_new()` calls `read_form()`, which puts the three boxes into a dictionary.
2. `send_request("/clothes/add", values)` turns the dictionary into bytes with `urlencode(...).encode("utf-8")` and calls `urlopen` with `data=`, so it sends a **POST**:
   ```
   POST http://127.0.0.1:5050/clothes/add
   name=Red+shemagh&min_temp=-10&max_temp=20
   ```
3. Flask runs `add_clothing()`. `read_clothing_form()` reads `request.form` and checks the values, then `db.add()` runs an `INSERT` with placeholders and commits.
4. Flask replies with status **201** and JSON:
   ```
   {"id": 4, "message": "Saved: Red shemagh"}
   ```
5. `send_request()` reads it with `json.loads`. The window reloads the table and shows "Saved: Red shemagh" in green.

If the name is empty, Flask replies with status **400** and `{"error": "Name is required."}`. `urlopen` raises `HTTPError`, `send_request()` catches it, reads Flask's JSON with `error.read()`, and the window shows the message in red.

## Test results

| # | Test | What I did | Expected result | Result |
|---|---|---|---|---|
| 1 | Add | Typed `Red shemagh`, `-10`, `20` → Save new | Appears in the table; "Saved: Red shemagh" in green | Pass |
| 2 | View | Looked at the table | All saved clothes shown with ID, name, min and max | Pass |
| 3 | Edit | Selected Red shemagh → changed Max to `22` → Update | "Updated: Red shemagh"; only that row changed | Pass |
| 4 | Delete, No | Selected Red shemagh → Delete → No | Nothing changed | Pass |
| 5 | Delete, Yes | Delete → Yes | "Delete 'Red shemagh'?" was asked; only that item disappeared | Pass |
| 6 | Missing input | Save new with an empty name | "Name is required." in red | Pass |
| 7 | Invalid value | Min = `abc` | "Min temperature must be a whole number." | Pass |
| 8 | Invalid value | Max = `80` | "Max temperature must be between -10 and 55." | Pass |
| 9 | Invalid value | Min = `30`, Max = `20` | "Min temperature cannot be higher than max temperature." | Pass |
| 10 | No selection | Update with nothing selected | "Select an item from the table first." | Pass |
| 11 | Forecast | Riyadh, current hour, temperature empty → شلبس؟ | "Riyadh at __:00 feels like __°C. Wear: …" | Pass |
| 12 | Forecast | Abha at hour 21 | Colder than Riyadh; suggests winter clothes | Pass |
| 13 | Typed temperature | Typed `30` → شلبس؟ | "You typed 30°C. Wear: Summer thobe" | Pass |
| 14 | Invalid value | Temperature `abc` | "Temperature must be a whole number." | Pass |
| 15 | No internet | Wi-Fi off, temperature empty → شلبس؟ | "Couldn't get the weather forecast…"; typing a temperature still works | Pass |
| 16 | Flask stopped | Stopped Flask → Refresh | "Can't reach the server…"; the window stayed open | Pass |
| 17 | Flask restarted | Started Flask → Refresh in the same window | Clothes loaded again without restarting the window | Pass |
| 18 | Data kept | Closed both, started both again | All saved clothes were still there | Pass |
| 19 | Unknown ID | Two windows, deleted an item in one, Update in the other | "Item __ was not found. It may have been deleted." | Pass |
| 20 | Empty list | Started with an empty database | "No clothes saved yet. Add your first item above." | Pass |
| 21 | Report | `python report.py` with Flask running | "Report saved…"; the file lists the clothes correctly | Pass |
| 22 | Report, no Flask | `python report.py` with Flask stopped | "Can't reach the server. Start Flask first…" | Pass |
| 23 | Report, file error | Made `wardrobe_report.txt` read-only → ran the report | "The report could not be saved: … Permission denied" | Pass |


## Credits

- **Weather data:** [Open-Meteo](https://open-meteo.com) free forecast API (no key required), licensed under CC BY 4.0.
- **Idea:** inspired by the website [shalbas.com](https://shalbas.com), which helps decide between summer and winter clothes. My app is my own design and code.
- **Libraries:** [Flask](https://flask.palletsprojects.com). Everything else (tkinter, sqlite3, urllib, json, threading, socket) is part of Python's standard library.
- **Course material:** patterns from the Advanced Programming 462 lectures (Tkinter window class, sqlite3 placeholders, Flask routes, threads).