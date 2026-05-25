from enum import Enum, auto

from engine import NLPEngine


class State(Enum):
    IDLE = auto()
    ORDERING = auto()
    CONFIRMATION = auto()
    PAYMENT = auto()


class CoffeeFSM:
    def __init__(self):
        self.state = State.IDLE
        self.nlp = NLPEngine()
        self.cart = []
        self.response = ""

    def get_response(self):
        return self.response

    def calculate_total(self):
        return sum(item["price"] * item["qty"] for item in self.cart)

    def get_menu_text(self):
        menu_lines = ["**Daftar Menu Logic Coffee:**", ""]
        for key, data in self.nlp.menu_data.items():
            menu_lines.append(
                f"- {data['emoji']} **{key.capitalize()}** (Rp {data['price']:,}): *{data['desc']}*"
            )
        menu_lines.append("")
        menu_lines.append("Silakan ketik pesanan Anda, misalnya: *Pesan 2 teh, 1 espresso*.")
        return "\n".join(menu_lines)

    def reduce_cart(self, item_to_reduce, qty_to_remove):
        for item in self.cart:
            if item["item"] != item_to_reduce:
                continue

            item["qty"] -= qty_to_remove
            if item["qty"] <= 0:
                self.cart.remove(item)
                return f"**{item_to_reduce}** telah dihapus dari keranjang."

            return f"**{item_to_reduce}** dikurangi {qty_to_remove}. Sisa: {item['qty']}."

        return f"Gagal: **{item_to_reduce}** tidak ditemukan di keranjang Anda."

    def step(self, user_input=""):
        user_input = user_input.strip()
        intent = self.nlp.detect_intent(user_input)

        if intent == "RESET_SYSTEM":
            self.__init__()
            self.response = "Sistem di-reset total. Halo! Mau pesan apa?"
            return

        if self.state == State.IDLE:
            if intent == "ASK_MENU":
                self.state = State.ORDERING
                self.response = self.get_menu_text()
                return
            if user_input:
                self.state = State.ORDERING
                self.step(user_input)
                return

            self.response = "Halo! Mau pesan apa hari ini? Ketik `menu` untuk melihat pilihan."
            return

        if self.state == State.ORDERING:
            if intent == "ASK_MENU":
                self.response = self.get_menu_text()
                return

            if intent == "CANCEL_ALL":
                self.cart = []
                self.response = "Keranjang telah dikosongkan. Mau pesan yang lain?"
                return

            if intent == "REDUCE_ITEM":
                items_to_remove = self.nlp.parse_orders(user_input)
                if items_to_remove:
                    self.response = "\n".join(
                        self.reduce_cart(item["item"], item["qty"]) for item in items_to_remove
                    )
                else:
                    self.response = "Item apa yang ingin dibatalkan? Contoh: *batalkan 1 kopi*."
                return

            if intent == "CHECKOUT":
                if not self.cart:
                    self.response = "Keranjang masih kosong."
                else:
                    self.state = State.CONFIRMATION
                    self.response = f"Total: **Rp {self.calculate_total():,}**. Lanjut bayar? (Ya/Tidak)"
                return

            new_orders = self.nlp.parse_orders(user_input)
            if new_orders:
                for order in new_orders:
                    existing = next((i for i in self.cart if i["item"] == order["item"]), None)
                    if existing:
                        existing["qty"] += order["qty"]
                    else:
                        self.cart.append(order)
                self.response = "Pesanan ditambahkan. Ada lagi? Ketik `bayar` untuk selesai."
            else:
                self.response = "Maaf, saya tidak mengerti. Coba: *pesan 2 kopi* atau *hapus 1 kopi*."
            return

        if self.state == State.CONFIRMATION:
            if intent == "YES":
                self.state = State.PAYMENT
                self.step()
            elif intent == "NO":
                self.state = State.ORDERING
                self.response = "Oke, silakan tambah pesanan lagi."
            else:
                self.response = "Jawab `Ya` atau `Tidak`."
            return

        if self.state == State.PAYMENT:
            total = self.calculate_total()
            self.response = f"Terima kasih! Pembayaran Rp {total:,} diterima. Pesanan diproses."
            self.cart = []
            self.state = State.IDLE
