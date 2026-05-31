import tkinter as tk
from tkinter import ttk, messagebox
import os
from db import get_conn
import styles

class MenuView:
    def __init__(self, app):
        self.app = app

    def show(self):
        self.app.create_page_header("Our Menu")
        
        container = tk.Frame(self.app.content_area, bg=styles.BG_COLOR, padx=30)
        container.pack(fill="both", expand=True)
        
        # Search & Filter Bar
        filter_bar = tk.Frame(container, bg=styles.BG_COLOR, pady=10)
        filter_bar.pack(fill="x")
        
        tk.Label(filter_bar, text="Search:", font=styles.SMALL_FONT, bg=styles.BG_COLOR).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.refresh_menu_list())
        search_entry = tk.Entry(filter_bar, textvariable=self.search_var, font=styles.SMALL_FONT, width=30)
        search_entry.pack(side="left", padx=10)
        
        # Scrollable Menu Area
        canvas = tk.Canvas(container, bg=styles.BG_COLOR, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg=styles.BG_COLOR)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=800)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.refresh_menu_list()

    def refresh_menu_list(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        search_term = self.search_var.get().lower()
        
        conn = get_conn()
        query = "SELECT id, item_name, category, price, stock, image_path FROM menu WHERE is_active = 1"
        if search_term:
            query += " AND (lower(item_name) LIKE ? OR lower(category) LIKE ?)"
            params = (f"%{search_term}%", f"%{search_term}%")
            items = conn.execute(query, params).fetchall()
        else:
            items = conn.execute(query).fetchall()
        conn.close()
        
        if not items:
            tk.Label(self.scrollable_frame, text="No items found.", font=styles.SUBHEADER_FONT, bg=styles.BG_COLOR, fg="#999").pack(pady=50)
            return

        for item in items:
            self.create_menu_item_card(item)

    def create_menu_item_card(self, item):
        id, name, category, price, stock, img_path = item
        
        card = tk.Frame(self.scrollable_frame, bg=styles.CARD_COLOR, pady=15, padx=20, highlightbackground="#eee", highlightthickness=1)
        card.pack(fill="x", pady=5, padx=5)
        
        # Image Section
        img_frame = tk.Frame(card, bg=styles.CARD_COLOR, width=80, height=80)
        img_frame.pack(side="left", padx=(0, 20))
        img_frame.pack_propagate(False)
        
        tk.Label(img_frame, text="🍴", font=("Segoe UI", 24), bg="#f0f0f0").pack(expand=True, fill="both")

        info_frame = tk.Frame(card, bg=styles.CARD_COLOR)
        info_frame.pack(side="left", fill="both", expand=True)
        
        tk.Label(info_frame, text=name, font=styles.SUBHEADER_FONT, bg=styles.CARD_COLOR, fg=styles.TEXT_COLOR).pack(anchor="w")
        tk.Label(info_frame, text=category, font=styles.SMALL_FONT, bg=styles.CARD_COLOR, fg="#888").pack(anchor="w")
        
        action_frame = tk.Frame(card, bg=styles.CARD_COLOR)
        action_frame.pack(side="right")
        
        tk.Label(action_frame, text=f"Rs.{price:.2f}", font=styles.SUBHEADER_FONT, bg=styles.CARD_COLOR, fg=styles.PRIMARY_COLOR).pack(side="left", padx=20)
        
        if stock > 0:
            add_btn = tk.Button(action_frame, text="+ Add to Cart", font=styles.SMALL_FONT, bg=styles.ACCENT_COLOR, fg="white", 
                               bd=0, padx=15, pady=5, cursor="hand2", command=lambda i=item: self.app.add_to_cart(i))
            add_btn.pack(side="left")
        else:
            tk.Label(action_frame, text="Out of Stock", font=styles.SMALL_FONT, fg="red", bg=styles.CARD_COLOR).pack(side="left")
