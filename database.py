import sqlite3

class Database:

    def __init__(self, path="wardrobe.db"):
        self.path = path
        self.create_table()

    def create_table(self):
        conn = sqlite3.connect(self.path)
        try:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS clothes ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "name TEXT NOT NULL, "
                "min_temp INTEGER NOT NULL, "
                "max_temp INTEGER NOT NULL)"
            )
        finally:
            conn.close()

    def row_to_dict(self, row):
        return {"id": row[0], "name": row[1], "min_temp": row[2], "max_temp": row[3]}

    def get_all(self):
        conn = sqlite3.connect(self.path)
        try:
            rows = conn.execute(
                "SELECT id, name, min_temp, max_temp FROM clothes ORDER BY id"
            ).fetchall()
        finally:
            conn.close()
        items = []
        for row in rows:
            items.append(self.row_to_dict(row))
        return items

    def get_for_temperature(self, temp):
        conn = sqlite3.connect(self.path)
        try:
            rows = conn.execute(
                "SELECT id, name, min_temp, max_temp FROM clothes "
                "WHERE min_temp <= ? AND max_temp >= ? ORDER BY id",
                (temp, temp),
            ).fetchall()
        finally:
            conn.close()
        items = []
        for row in rows:
            items.append(self.row_to_dict(row))
        return items

    def add(self, name, min_temp, max_temp):
        conn = sqlite3.connect(self.path)
        try:
            cur = conn.execute(
                "INSERT INTO clothes (name, min_temp, max_temp) VALUES (?, ?, ?)",
                (name, min_temp, max_temp),
            )
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()

    def update(self, item_id, name, min_temp, max_temp):
        conn = sqlite3.connect(self.path)
        try:
            cur = conn.execute(
                "UPDATE clothes SET name = ?, min_temp = ?, max_temp = ? WHERE id = ?",
                (name, min_temp, max_temp, item_id),
            )
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()

    def delete(self, item_id):
        conn = sqlite3.connect(self.path)
        try:
            cur = conn.execute("DELETE FROM clothes WHERE id = ?", (item_id,))
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()


if __name__ == "__main__":
    # Table setup: run "python database.py" to create the table.
    # Existing records are kept. Sample clothes are added only if the table is empty.
    db = Database()
    if len(db.get_all()) == 0:
        db.add("Summer thobe", 24, 50)
        db.add("Winter thobe", -10, 23)
        db.add("Jacket", -10, 17)
        print("Table created and 3 sample clothes added.")
    else:
        print("Table already exists. Your saved clothes were kept.")
    for item in db.get_all():
        print(item)