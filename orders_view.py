import tkinter as tk
from db import get_conn
import styles

class OrdersView:
    def __init__(self, app):
        self.app = app

    def show(self):
        self.app.create_page_header("My Order History")
        container = tk.Frame(self.app.content_area, bg=styles.BG_COLOR, padx=30)
        container.pack(fill="both", expand=True)
        
        conn = get_conn()
        user_id = self.app.current_user['id']
        orders = conn.execute("SELECT id, total_amount, payment_method, date_time FROM orders WHERE customer_id = ? ORDER BY date_time DESC", (user_id,)).fetchall()
        conn.close()
        
        if not orders:
            tk.Label(container, text="No orders yet.", font=styles.SUBHEADER_FONT, bg=styles.BG_COLOR, fg="#999").pack(pady=100)
            return

        for o in orders:
            o_card = tk.Frame(container, bg=styles.CARD_COLOR, pady=15, padx=20, highlightbackground="#eee", highlightthickness=1)
            o_card.pack(fill="x", pady=5)
            
            tk.Label(o_card, text=f"Order ID: #{o[0]}", font=styles.SUBHEADER_FONT, bg=styles.CARD_COLOR).pack(side="left")
            tk.Label(o_card, text=f"Amount: Rs.{o[1]:.2f}", font=styles.NORMAL_FONT, bg=styles.CARD_COLOR, padx=20).pack(side="left")
            tk.Label(o_card, text=f"Paid via: {o[2]}", font=styles.SMALL_FONT, bg=styles.CARD_COLOR).pack(side="left")
            tk.Label(o_card, text=o[3], font=styles.SMALL_FONT, bg=styles.CARD_COLOR, fg="#999").pack(side="right")
