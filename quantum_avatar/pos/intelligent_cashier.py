import xml.etree.ElementTree as ET


class IntelligentCashier:
    def __init__(self):
        self.sales = {"food": 1000, "non_food": 500}  # CHF

    def calculate_vat(self):
        vat_2_6 = self.sales["food"] * 0.026
        vat_8_1 = self.sales["non_food"] * 0.081
        return vat_2_6, vat_8_1

    def generate_xml(self, filename="daily_close.xml"):
        vat_2_6, vat_8_1 = self.calculate_vat()
        root = ET.Element("DailyClose")
        ET.SubElement(root, "TotalSales").text = str(sum(self.sales.values()))
        ET.SubElement(root, "VAT_2_6").text = str(vat_2_6)
        ET.SubElement(root, "VAT_8_1").text = str(vat_8_1)
        tree = ET.ElementTree(root)
        tree.write(filename)

    def top_seller_analysis(self):
        # Mock
        return "Top-Seller: Sucuk mit CHF 200 Marge"
