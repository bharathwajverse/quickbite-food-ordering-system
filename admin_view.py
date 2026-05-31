import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import shutil
import requests
import os
import sqlite3
from db import get_conn
import styles

class AdminView:
    def __init__(self, app):
        self.app = app
        self.new_image_path = ""
        self.new_url_var = None

    def show_analytics(self):
        self.app.create_page_header("Business Analytics")
        container = tk.Frame(self.app.content_area, bg=styles.BG_COLOR, padx=30)
        container.pack(fill="both", expand=True)
        
        conn = get_conn()
        sales = conn.execute("SELECT item_name, total_qty_sold, total_revenue FROM sales_report").fetchall()
        conn.close()
        
        stats_frame = tk.Frame(container, bg=styles.BG_COLOR)
        stats_frame.pack(fill="x", pady=10)
        
        total_rev = sum(s[2] for s in sales if s[2])
        self.create_stat_card(stats_frame, "Total Revenue", f"Rs.{total_rev:.2f}", styles.PRIMARY_COLOR).pack(side="left", padx=10)
        self.create_stat_card(stats_frame, "Top Selling Item", sales[0][0] if sales else "N/A", styles.ACCENT_COLOR).pack(side="left", padx=10)

        tk.Label(container, text="Sales by Item", font=styles.SUBHEADER_FONT, bg=styles.BG_COLOR).pack(anchor="w", pady=(20, 10))
        table = tk.Frame(container, bg=styles.CARD_COLOR, highlightbackground="#eee", highlightthickness=1)
        table.pack(fill="x")
        
        headers = ["Item Name", "Quantity Sold", "Revenue Generated"]
        for i, h in enumerate(headers):
            tk.Label(table, text=h, font=styles.SUBHEADER_FONT, bg="#f9f9f9", padx=10, pady=10).grid(row=0, column=i, sticky="nsew")
            
        for idx, row in enumerate(sales, 1):
            tk.Label(table, text=row[0], font=styles.NORMAL_FONT, bg=styles.CARD_COLOR, padx=10, pady=5).grid(row=idx, column=0, sticky="w")
            tk.Label(table, text=row[1], font=styles.NORMAL_FONT, bg=styles.CARD_COLOR, padx=10, pady=5).grid(row=idx, column=1)
            tk.Label(table, text=f"Rs.{row[2]:.2f}", font=styles.NORMAL_FONT, bg=styles.CARD_COLOR, padx=10, pady=5).grid(row=idx, column=2)

    def create_stat_card(self, parent, label, value, color):
        card = tk.Frame(parent, bg=styles.CARD_COLOR, padx=20, pady=20, highlightbackground="#eee", highlightthickness=1, width=200)
        card.pack_propagate(False)
        tk.Label(card, text=label, font=styles.SMALL_FONT, fg="#666", bg=styles.CARD_COLOR).pack()
        tk.Label(card, text=value, font=styles.SUBHEADER_FONT, fg=color, bg=styles.CARD_COLOR).pack(pady=5)
        return card

    def show_panel(self):
        self.app.create_page_header("Administrative Panel")
        container = tk.Frame(self.app.content_area, bg=styles.BG_COLOR, padx=30)
        container.pack(fill="both", expand=True)
        
        tk.Label(container, text="Manage Menu Items", font=styles.SUBHEADER_FONT, bg=styles.BG_COLOR).pack(anchor="w", pady=10)
        
        # Add new item form
        add_frame = tk.Frame(container, bg=styles.CARD_COLOR, pady=20, padx=20, highlightbackground="#eee", highlightthickness=1)
        add_frame.pack(fill="x")
        
        tk.Label(add_frame, text="Name:", bg=styles.CARD_COLOR).grid(row=0, column=0, padx=5, pady=5)
        self.new_name = tk.Entry(add_frame)
        self.new_name.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(add_frame, text="Category:", bg=styles.CARD_COLOR).grid(row=0, column=2, padx=5, pady=5)
        
        # Fetch existing categories for dropdown
        conn = get_conn()
        categories = [r[0] for r in conn.execute("SELECT DISTINCT category FROM menu").fetchall()]
        conn.close()
        
        self.new_cat = ttk.Combobox(add_frame, values=categories)
        self.new_cat.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(add_frame, text="Price:", bg=styles.CARD_COLOR).grid(row=1, column=0, padx=5, pady=5)
        self.new_price = tk.Entry(add_frame)
        self.new_price.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(add_frame, text="Stock:", bg=styles.CARD_COLOR).grid(row=1, column=2, padx=5, pady=5)
        self.new_stock = tk.Entry(add_frame)
        self.new_stock.grid(row=1, column=3, padx=5, pady=5)
        
        tk.Label(add_frame, text="Image URL:", bg=styles.CARD_COLOR).grid(row=2, column=0, padx=5, pady=5)
        self.new_url_var = tk.Entry(add_frame, width=30)
        self.new_url_var.grid(row=2, column=1, padx=5, pady=5)
        
        tk.Label(add_frame, text="OR", font=styles.SMALL_FONT, bg=styles.CARD_COLOR).grid(row=2, column=2)
        self.add_img_btn = tk.Button(add_frame, text="Select File", font=styles.SMALL_FONT, command=self.select_add_image)
        self.add_img_btn.grid(row=2, column=3, padx=5, pady=5)
        
        add_btn = tk.Button(add_frame, text="Add Item", bg=styles.ACCENT_COLOR, fg="white", bd=0, padx=20, pady=5, 
                            command=self.add_menu_item)
        add_btn.grid(row=3, column=0, columnspan=4, pady=10)

        # Update existing items section
        tk.Label(container, text="Update Existing Items", font=styles.SUBHEADER_FONT, bg=styles.BG_COLOR).pack(anchor="w", pady=(30, 10))
        
        update_frame = tk.Frame(container, bg=styles.CARD_COLOR, pady=20, padx=20, highlightbackground="#eee", highlightthickness=1)
        update_frame.pack(fill="x")
        
        conn = get_conn()
        self.menu_items = conn.execute("SELECT id, item_name, price, stock FROM menu WHERE is_active = 1").fetchall()
        conn.close()
        
        if not self.menu_items:
            tk.Label(update_frame, text="No items to display.", bg=styles.CARD_COLOR).pack()
            return

        tk.Label(update_frame, text="Select Item:", bg=styles.CARD_COLOR).grid(row=0, column=0, padx=5, pady=5)
        self.selected_item_var = tk.StringVar()
        item_names = [f"{item[1]} (ID: {item[0]})" for item in self.menu_items]
        self.item_dropdown = ttk.Combobox(update_frame, textvariable=self.selected_item_var, values=item_names, state="readonly", width=30)
        self.item_dropdown.grid(row=0, column=1, padx=5, pady=5)
        self.item_dropdown.bind("<<ComboboxSelected>>", self.on_item_select_to_edit)
        
        tk.Label(update_frame, text="New Price:", bg=styles.CARD_COLOR).grid(row=1, column=0, padx=5, pady=5)
        self.edit_price_entry = tk.Entry(update_frame)
        self.edit_price_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(update_frame, text="New Stock:", bg=styles.CARD_COLOR).grid(row=1, column=2, padx=5, pady=5)
        self.edit_stock_entry = tk.Entry(update_frame)
        self.edit_stock_entry.grid(row=1, column=3, padx=5, pady=5)
        
        update_btn = tk.Button(update_frame, text="Save Changes", bg=styles.PRIMARY_COLOR, fg="white", bd=0, padx=20, pady=5, 
                               command=self.update_menu_item)
        update_btn.grid(row=2, column=0, columnspan=2, pady=15)

        remove_btn = tk.Button(update_frame, text="Remove Item", bg="#ff5252", fg="white", bd=0, padx=20, pady=5, 
                               command=self.remove_menu_item)
        remove_btn.grid(row=2, column=2, columnspan=2, pady=15)

    def select_add_image(self):
        self.new_image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif;*.webp"), ("All files", "*.*")])
        if self.new_image_path:
            self.add_img_btn.config(text="Image Selected ✓")



    def _save_image_to_assets(self, source, item_name):
        """Copies from local file OR downloads from URL to the assets folder."""
        if not source:
            return None
        
        assets_dir = "assets"
        if not os.path.exists(assets_dir):
            os.makedirs(assets_dir)
            
        # Create a safe filename
        safe_name = "".join([c for c in item_name if c.isalnum()]).lower()
        
        if source.startswith("http"):
            # It's a URL, download it
            try:
                response = requests.get(source, stream=True, timeout=10)
                if response.status_code == 200:
                    # Try to guess extension
                    ext = ".png" # default
                    if "image/jpeg" in response.headers.get("Content-Type", ""): ext = ".jpg"
                    elif "image/gif" in response.headers.get("Content-Type", ""): ext = ".gif"
                    
                    target_path = os.path.join(assets_dir, f"{safe_name}{ext}")
                    with open(target_path, 'wb') as f:
                        shutil.copyfileobj(response.raw, f)
                    return target_path.replace("\\", "/")
                else:
                    print(f"Failed to download image: {response.status_code}")
                    return None
            except Exception as e:
                print(f"Error downloading image: {e}")
                return None
        else:
            # It's a local file
            ext = os.path.splitext(source)[1]
            target_path = os.path.join(assets_dir, f"{safe_name}{ext}")
            try:
                shutil.copy2(source, target_path)
                return target_path.replace("\\", "/")
            except Exception:
                return source

    def add_menu_item(self):
        name = self.new_name.get().strip()
        cat = self.new_cat.get().strip()
        price = self.new_price.get().strip()
        stock = self.new_stock.get().strip()
        url = self.new_url_var.get().strip()
        
        if not (name and cat and price and stock):
            messagebox.showwarning("Incomplete", "Please fill all fields")
            return
            
        conn = get_conn()
        existing = conn.execute("SELECT id, is_active FROM menu WHERE lower(item_name) = lower(?)", (name,)).fetchone()
        
        if existing and existing[1] == 1:
            conn.close()
            messagebox.showwarning("Duplicate Item", f"An item named '{name}' already exists!")
            return

        # Decide source: Prefer URL if provided, otherwise local file
        source = url if url else self.new_image_path
        final_image_path = self._save_image_to_assets(source, name)
        
        if existing and existing[1] == 0:
            # Reactivate and update existing inactive item
            conn.execute("UPDATE menu SET category=?, price=?, stock=?, image_path=?, is_active=1 WHERE id=?",
                         (cat, float(price), int(stock), final_image_path, existing[0]))
        else:
            conn.execute("INSERT INTO menu (item_name, category, price, stock, image_path) VALUES (?,?,?,?,?)",
                         (name, cat, float(price), int(stock), final_image_path))
            
        conn.commit()
        conn.close()
        
        messagebox.showinfo("Success", f"{name} added to menu!")
        self.new_image_path = ""
        self.show_panel()

    def on_item_select_to_edit(self, event):
        selected_str = self.selected_item_var.get()
        item_id = int(selected_str.split("ID: ")[1].replace(")", ""))
        for item in self.menu_items:
            if item[0] == item_id:
                self.edit_price_entry.delete(0, 'end')
                self.edit_price_entry.insert(0, str(item[2]))
                self.edit_stock_entry.delete(0, 'end')
                self.edit_stock_entry.insert(0, str(item[3]))
                break

    def update_menu_item(self):
        selected_str = self.selected_item_var.get()
        if not selected_str: return
        item_id = int(selected_str.split("ID: ")[1].replace(")", ""))
        new_price = self.edit_price_entry.get()
        new_stock = self.edit_stock_entry.get()
        try:
            conn = get_conn()
            conn.execute("UPDATE menu SET price = ?, stock = ? WHERE id = ?", 
                         (float(new_price), int(new_stock), item_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Item updated successfully!")
            self.show_panel()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def remove_menu_item(self):
        selected_str = self.selected_item_var.get()
        if not selected_str:
            messagebox.showwarning("Warning", "Please select an item to remove")
            return
            
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to remove this item?")
        if not confirm: return
        
        item_id = int(selected_str.split("ID: ")[1].replace(")", ""))
        
        try:
            conn = get_conn()
            conn.execute("UPDATE menu SET is_active = 0 WHERE id = ?", (item_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Item removed successfully!")
            self.show_panel()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_coupons_panel(self):
        self.app.create_page_header("Manage Coupons")
        container = tk.Frame(self.app.content_area, bg=styles.BG_COLOR, padx=30)
        container.pack(fill="both", expand=True)

        tk.Label(container, text="Create New Coupon", font=styles.SUBHEADER_FONT, bg=styles.BG_COLOR).pack(anchor="w", pady=10)
        
        add_frame = tk.Frame(container, bg=styles.CARD_COLOR, pady=20, padx=20, highlightbackground="#eee", highlightthickness=1)
        add_frame.pack(fill="x")
        
        tk.Label(add_frame, text="Coupon Code:", bg=styles.CARD_COLOR).grid(row=0, column=0, padx=5, pady=5)
        self.new_coupon_code = tk.Entry(add_frame)
        self.new_coupon_code.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(add_frame, text="Discount (%):", bg=styles.CARD_COLOR).grid(row=0, column=2, padx=5, pady=5)
        self.new_coupon_discount = tk.Entry(add_frame)
        self.new_coupon_discount.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(add_frame, text="Max Uses:", bg=styles.CARD_COLOR).grid(row=1, column=0, padx=5, pady=5)
        self.new_coupon_max = tk.Entry(add_frame)
        self.new_coupon_max.insert(0, "100")
        self.new_coupon_max.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(add_frame, text="Expiry Date (YYYY-MM-DD):", bg=styles.CARD_COLOR).grid(row=1, column=2, padx=5, pady=5)
        self.new_coupon_expiry = tk.Entry(add_frame)
        self.new_coupon_expiry.grid(row=1, column=3, padx=5, pady=5)
        
        add_btn = tk.Button(add_frame, text="Create Coupon", bg=styles.ACCENT_COLOR, fg="white", bd=0, padx=20, pady=5, 
                            command=self.add_coupon)
        add_btn.grid(row=2, column=0, columnspan=4, pady=10)

        # Show existing coupons
        tk.Label(container, text="Active Coupons", font=styles.SUBHEADER_FONT, bg=styles.BG_COLOR).pack(anchor="w", pady=(30, 10))
        
        table = tk.Frame(container, bg=styles.CARD_COLOR, highlightbackground="#eee", highlightthickness=1)
        table.pack(fill="x")
        
        headers = ["Code", "Discount", "Max Uses", "Used Count", "Expiry", "Actions"]
        for i, h in enumerate(headers):
            tk.Label(table, text=h, font=styles.SUBHEADER_FONT, bg="#f9f9f9", padx=10, pady=10).grid(row=0, column=i, sticky="nsew")
            
        conn = get_conn()
        coupons = conn.execute("SELECT code, discount_percentage, max_uses, used_count, expires_on FROM coupons").fetchall()
        conn.close()
        
        for idx, row in enumerate(coupons, 1):
            tk.Label(table, text=row[0], font=styles.NORMAL_FONT, bg=styles.CARD_COLOR, padx=10, pady=5).grid(row=idx, column=0, sticky="w")
            tk.Label(table, text=f"{row[1]}%", font=styles.NORMAL_FONT, bg=styles.CARD_COLOR, padx=10, pady=5).grid(row=idx, column=1)
            tk.Label(table, text=row[2], font=styles.NORMAL_FONT, bg=styles.CARD_COLOR, padx=10, pady=5).grid(row=idx, column=2)
            tk.Label(table, text=row[3], font=styles.NORMAL_FONT, bg=styles.CARD_COLOR, padx=10, pady=5).grid(row=idx, column=3)
            tk.Label(table, text=row[4] if row[4] else "Never", font=styles.NORMAL_FONT, bg=styles.CARD_COLOR, padx=10, pady=5).grid(row=idx, column=4)
            
            del_btn = tk.Button(table, text="Delete", font=styles.SMALL_FONT, bg="#ff5252", fg="white", bd=0, 
                                command=lambda c=row[0]: self.delete_coupon(c))
            del_btn.grid(row=idx, column=5, padx=5, pady=5)

    def add_coupon(self):
        code = self.new_coupon_code.get().strip().upper()
        discount = self.new_coupon_discount.get().strip()
        max_uses = self.new_coupon_max.get().strip()
        expiry = self.new_coupon_expiry.get().strip()
        
        if not code or not discount:
            messagebox.showwarning("Incomplete", "Code and Discount are required fields.")
            return
            
        try:
            discount = float(discount)
            max_uses = int(max_uses) if max_uses else 100
            
            conn = get_conn()
            try:
                conn.execute("INSERT INTO coupons (code, discount_percentage, max_uses, expires_on) VALUES (?,?,?,?)",
                             (code, discount, max_uses, expiry if expiry else None))
                conn.commit()
                messagebox.showinfo("Success", f"Coupon {code} created successfully!")
                self.show_coupons_panel()
            except sqlite3.IntegrityError:
                messagebox.showwarning("Duplicate", f"Coupon {code} already exists.")
            finally:
                conn.close()
        except ValueError:
            messagebox.showwarning("Invalid Input", "Discount and Max Uses must be numbers.")
            
    def delete_coupon(self, code):
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete coupon {code}?"):
            conn = get_conn()
            conn.execute("DELETE FROM coupons WHERE code = ?", (code,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Deleted", "Coupon deleted successfully!")
            self.show_coupons_panel()
