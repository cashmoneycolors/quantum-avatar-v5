import csv


class ManagementDashboard:
    def __init__(self):
        self.sales = 1500.50  # CHF
        self.inventory_turnover = {"sucuk": 5, "gemuese": 8}
        self.customer_satisfaction = 4.8

    def display_kpis(self):
        print(f"Tagesumsatz: CHF {self.sales}")
        print(f"Lagerumschlag: {self.inventory_turnover}")
        print(f"Kundenzufriedenheit: {self.customer_satisfaction}")

    def export_csv(self, filename="report.csv"):
        with open(filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["KPI", "Wert"])
            writer.writerow(["Tagesumsatz CHF", self.sales])
            writer.writerow(["Sucuk Umschlag", self.inventory_turnover["sucuk"]])
            writer.writerow(["Gemüse Umschlag", self.inventory_turnover["gemuese"]])
            writer.writerow(["Kundenzufriedenheit", self.customer_satisfaction])
