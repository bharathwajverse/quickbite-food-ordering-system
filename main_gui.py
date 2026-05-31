import tkinter as tk
from tkinter import ttk, messagebox
import styles
from db import setup_db
from auth_view import AuthView
from menu_view import MenuView
from cart_view import CartView
from review_view import ReviewView
from admin_view import AdminView
from orders_view import OrdersView

class QuickBiteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QuickBite - Smart Food Ordering System")
        self.root.geometry("1100x700")
        self.root.configure(bg=styles.BG_COLOR)
        
        # Initialize Views
        self.auth_view = AuthView(self)
        self.menu_view = MenuView(self)
        self.cart_view = CartView(self)
        self.review_view = ReviewView(self)
        self.admin_view = AdminView(self)
        self.orders_view = OrdersView(self)
        
        # State
        self.current_user = None
        self.cart = [] 
        
        setup_db()
        self.auth_view.show_login()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_main_dashboard(self):
        self.clear_screen()
        
        # Sidebar
        self.sidebar = tk.Frame(self.root, bg=styles.SECONDARY_COLOR, width=250)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        self.content_area = tk.Frame(self.root, bg=styles.BG_COLOR)
        self.content_area.pack(side="right", expand=True, fill="both")
        
        tk.Label(self.sidebar, text="QuickBite", font=("Segoe UI", 20, "bold"), fg=styles.PRIMARY_COLOR, bg=styles.SECONDARY_COLOR, pady=30).pack()
        
        nav_items = [
            ("Menu", self.menu_view.show),
            ("My Cart", self.cart_view.show),
            ("Reviews", self.review_view.show),
            ("My Orders", self.orders_view.show)
        ]
        
        if self.current_user['role'] == 'admin':
            nav_items.append(("Analytics", self.admin_view.show_analytics))
            nav_items.append(("Admin Panel", self.admin_view.show_panel))
            nav_items.append(("Coupons", self.admin_view.show_coupons_panel))
            
        for text, command in nav_items:
            btn = tk.Button(self.sidebar, text=text, font=styles.NORMAL_FONT, bg=styles.SECONDARY_COLOR, fg="white", 
                            bd=0, activebackground="#333", activeforeground=styles.PRIMARY_COLOR, 
                            anchor="w", padx=30, pady=15, cursor="hand2", command=command)
            btn.pack(fill="x")
            
        tk.Frame(self.sidebar, height=2, bg="#444").pack(side="bottom", fill="x", pady=10)
        logout_btn = tk.Button(self.sidebar, text="Logout", font=styles.NORMAL_FONT, bg=styles.SECONDARY_COLOR, fg="#ff5252", 
                               bd=0, activebackground="#333", activeforeground="#ff5252", 
                               anchor="w", padx=30, pady=15, cursor="hand2", command=self.auth_view.show_login)
        logout_btn.pack(side="bottom", fill="x")
        
        self.menu_view.show()

    def create_page_header(self, title):
        for widget in self.content_area.winfo_children():
            widget.destroy()
            
        header_frame = tk.Frame(self.content_area, bg=styles.BG_COLOR, pady=20, padx=30)
        header_frame.pack(fill="x")
        
        tk.Label(header_frame, text=title, font=styles.HEADER_FONT, bg=styles.BG_COLOR, fg=styles.TEXT_COLOR).pack(side="left")
        
        tk.Label(header_frame, text=f"Logged in as: {self.current_user['username']} ({self.current_user['role']})", 
                             font=styles.SMALL_FONT, bg=styles.BG_COLOR, fg="#666").pack(side="right", pady=10)

    def add_to_cart(self, item):
        id, name, category, price, stock = item[:5]
        for cart_item in self.cart:
            if cart_item['id'] == id:
                cart_item['quantity'] += 1
                messagebox.showinfo("Success", f"Added another {name} to cart!")
                return
        
        self.cart.append({'id': id, 'name': name, 'price': price, 'quantity': 1})
        messagebox.showinfo("Success", f"{name} added to cart!")

if __name__ == "__main__":
    root = tk.Tk()
    app = QuickBiteApp(root)
    root.mainloop()
