import re


class NLPEngine:
    def __init__(self):
        self.menu_data = {
            "kopi": {"price": 15000, "emoji": "☕", "desc": "Kopi hitam klasik"},
            "latte": {"price": 20000, "emoji": "🥛", "desc": "Espresso dengan susu steamed"},
            "teh": {"price": 10000, "emoji": "🍵", "desc": "Teh melati hangat"},
            "espresso": {"price": 18000, "emoji": "⚡", "desc": "Shot kopi murni pekat"},
        }

        menu_keys = "|".join(self.menu_data.keys())
        self.re_number = r"\b(\d+)\b"
        self.re_menu = rf"\b({menu_keys})\b"
        self.re_split = r"[,.]|\bdan\b|\b&\b"
        self.re_cancel_all = r"\b(batalkan semua|hapus semua|reset keranjang|kosongkan)\b"
        self.re_reduce = r"\b(batalkan|kurangi|tidak jadi|hapus|cancel)\b"

    def _parse_single_segment(self, text):
        text = text.lower().strip()
        item_match = re.search(self.re_menu, text)
        if not item_match:
            return None

        item_key = item_match.group(1)
        qty_match = re.search(self.re_number, text)
        qty = int(qty_match.group(1)) if qty_match else 1

        return {
            "item": item_key,
            "qty": qty,
            "price": self.menu_data[item_key]["price"],
            "emoji": self.menu_data[item_key]["emoji"],
        }

    def parse_orders(self, full_text):
        segments = re.split(self.re_split, full_text.lower())
        found_orders = []

        for segment in segments:
            if not segment.strip():
                continue
            order = self._parse_single_segment(segment)
            if order:
                found_orders.append(order)

        return found_orders

    def detect_intent(self, text):
        text = text.lower()
        if re.search(r"\b(reset|ulang|restart)\b", text):
            return "RESET_SYSTEM"
        if re.search(self.re_cancel_all, text):
            return "CANCEL_ALL"
        if re.search(self.re_reduce, text):
            return "REDUCE_ITEM"
        if re.search(r"\b(menu|daftar|apa saja|jual apa|list)\b", text):
            return "ASK_MENU"
        if re.search(r"\b(selesai|bayar|checkout|cukup)\b", text):
            return "CHECKOUT"
        if re.search(r"\b(ya|yes|oke|ok|betul|siap|baik)\b", text):
            return "YES"
        if re.search(r"\b(tidak|enggak|nggak|batal|no|salah)\b", text):
            return "NO"
        return "UNKNOWN"


BotPesanan = NLPEngine
