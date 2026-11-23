# What-to-Wear
Saeed Abdullah Muathin – 451000383

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