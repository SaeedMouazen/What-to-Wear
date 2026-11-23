import json
import socket
import threading
from datetime import datetime
from urllib.error import URLError
from urllib.request import urlopen

SERVER = "http://127.0.0.1:5050"
REPORT_FILE = "wardrobe_report.txt"


def get_clothes():
    """Ask Flask's JSON route for the saved clothes. Returns a list, or None if Flask can't be reached."""
    try:
        with urlopen(SERVER + "/clothes", timeout=5) as reply:
            return json.loads(reply.read().decode("utf-8"))
    except (URLError, socket.timeout):
        return None


def write_report(clothes, result):
    """Runs in the thread. Writes the report file and puts the outcome in the result dictionary."""
    try:
        with open(REPORT_FILE, "w", encoding="utf-8") as file:
            file.write("شلبس؟ What to Wear - Wardrobe Report\n")
            file.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            file.write(f"Number of items: {len(clothes)}\n")
            file.write("-" * 45 + "\n")
            if len(clothes) == 0:
                file.write("No clothes saved yet.\n")
            for item in clothes:
                file.write(f"{item['id']:>3}. {item['name']:<25} {item['min_temp']}°C to {item['max_temp']}°C\n")
        result["saved"] = True
    except OSError as error:
        result["error"] = str(error)


def main():
    clothes = get_clothes()
    if clothes is None:
        print("Can't reach the server. Start Flask first with: python server.py")
        return

    result = {"saved": False, "error": ""}
    thread = threading.Thread(target=write_report, args=(clothes, result))
    thread.start()
    print("Writing the report in a separate thread...")
    thread.join()

    if result["saved"]:
        print(f"Report saved to {REPORT_FILE} ({len(clothes)} items).")
    else:
        print(f"The report could not be saved: {result['error']}")


if __name__ == "__main__":
    main()