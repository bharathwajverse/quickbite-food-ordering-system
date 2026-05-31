import tkinter as tk
from tkinter import messagebox
import uuid
from datetime import datetime
from db import get_conn
import styles

class CartView:
    def __init__(self, app):
        self.app = app

    def show(self):
        self.app.create_page_header("Your Shopping Cart")
        
        container = tk.Frame(self.app.content_area, bg=styles.BG_COLOR, padx=30)
        container.pack(fill="both", expand=True)
        
        if not self.app.cart:
            tk.Label(container, text="Your cart is empty. Start adding some delicious food!", 
                     font=styles.SUBHEADER_FONT, bg=styles.BG_COLOR, fg="#999").pack(pady=100)
            return
            
        cart_table = tk.Frame(container, bg=styles.CARD_COLOR, highlightbackground="#eee", highlightthickness=1)
        cart_table.pack(fill="x", pady=20)
        
        headers = ["Item", "Price", "Qty", "Subtotal", "Actions"]
        for i, header in enumerate(headers):
            tk.Label(cart_table, text=header, font=styles.SUBHEADER_FONT, bg="#f9f9f9", padx=10, pady=10).grid(row=0, column=i, sticky="nsew")
            
        total_amount = 0
        for idx, item in enumerate(self.app.cart, 1):
            subtotal = item['price'] * item['quantity']
            total_amount += subtotal
            
            tk.Label(cart_table, text=item['name'], font=styles.NORMAL_FONT, bg=styles.CARD_COLOR, padx=10, pady=10).grid(row=idx, column=0, sticky="w")
            tk.Label(cart_table, text=f"Rs.{item['price']:.2f}", font=styles.NORMAL_FONT, bg=styles.CARD_COLOR, padx=10, pady=10).grid(row=idx, column=1)
            tk.Label(cart_table, text=item['quantity'], font=styles.NORMAL_FONT, bg=styles.CARD_COLOR, padx=10, pady=10).grid(row=idx, column=2)
            tk.Label(cart_table, text=f"Rs.{subtotal:.2f}", font=styles.NORMAL_FONT, bg=styles.CARD_COLOR, padx=10, pady=10).grid(row=idx, column=3)
            
            remove_btn = tk.Button(cart_table, text="Remove", font=styles.SMALL_FONT, fg="red", bg=styles.CARD_COLOR, bd=0, 
                                   command=lambda i=idx-1: self.remove_item(i))
            remove_btn.grid(row=idx, column=4)

        summary_frame = tk.Frame(container, bg=styles.BG_COLOR, pady=20)
        summary_frame.pack(fill="x")
        
        tk.Label(summary_frame, text=f"Total Amount: Rs.{total_amount:.2f}", font=styles.HEADER_FONT, bg=styles.BG_COLOR, fg=styles.SECONDARY_COLOR).pack(side="right")
        
        checkout_btn = tk.Button(summary_frame, text="Proceed to Checkout", font=styles.SUBHEADER_FONT, bg=styles.PRIMARY_COLOR, fg="white", 
                                 bd=0, padx=30, pady=10, cursor="hand2", command=self.process_checkout)
        checkout_btn.pack(side="left")

    def remove_item(self, index):
        if 0 <= index < len(self.app.cart):
            del self.app.cart[index]
            self.show()

    def process_checkout(self):
        if not self.app.cart: return
        
        total = sum(item['price'] * item['quantity'] for item in self.app.cart)
        coupon_code = None
        
        has_coupon = messagebox.askyesno("Coupon", "Do you have a discount coupon?")
        if has_coupon:
            from tkinter import simpledialog
            code = simpledialog.askstring("Coupon", "Enter coupon code:")
            if code:
                conn = get_conn()
                coupon = conn.execute("SELECT discount_percentage, used_count, max_uses FROM coupons WHERE code = ?", (code.upper(),)).fetchone()
                conn.close()
                if coupon:
                    if coupon[1] < coupon[2]:
                        discount_percent = coupon[0]
                        coupon_code = code.upper()
                        discount_amount = total * (discount_percent / 100)
                        total -= discount_amount
                        messagebox.showinfo("Coupon Applied", f"{discount_percent}% discount applied! You saved Rs.{discount_amount:.2f}.")
                    else:
                        messagebox.showerror("Invalid Coupon", "This coupon has reached its maximum usage limit.")
                else:
                    messagebox.showerror("Invalid Coupon", "Coupon code not found or invalid.")

        payment_method = messagebox.askquestion("Payment", "Do you want to pay online?")
        method = "Online" if payment_method == "yes" else "Cash"
        
        order_id = str(uuid.uuid4())[:8].upper()
        date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        conn = get_conn()
        customer_id = self.app.current_user['id']
        
        conn.execute("INSERT INTO orders (id, customer_id, total_amount, payment_method, coupon_used, date_time) VALUES (?,?,?,?,?,?)",
                     (order_id, customer_id, total, method, coupon_code, date_time))
        
        if coupon_code:
            conn.execute("UPDATE coupons SET used_count = used_count + 1 WHERE code = ?", (coupon_code,))
        
        for item in self.app.cart:
            conn.execute("INSERT INTO order_items (order_id, menu_id, item_name, quantity, price_at_order) VALUES (?,?,?,?,?)",
                         (order_id, item['id'], item['name'], item['quantity'], item['price']))
            conn.execute("UPDATE menu SET stock = stock - ? WHERE id = ?", (item['quantity'], item['id']))
            
        conn.commit()
        conn.close()
        
        messagebox.showinfo("Order Confirmed", f"Order {order_id} placed successfully!\nTotal: Rs.{total:.2f}")
        self.app.cart = []
        self.app.orders_view.show()
