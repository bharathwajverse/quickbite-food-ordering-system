import tkinter as tk
from tkinter import messagebox
import os
from db import get_conn
import styles

class AuthView:
    def __init__(self, app):
        self.app = app

    def show_login(self):
        self.app.clear_screen()
        
        login_frame = tk.Frame(self.app.root, bg=styles.CARD_COLOR, padx=40, pady=40, highlightbackground="#ddd", highlightthickness=1)
        login_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Logo
        tk.Label(login_frame, text="QuickBite", font=("Segoe UI", 32, "bold"), fg=styles.PRIMARY_COLOR, bg=styles.CARD_COLOR).pack(pady=(0, 10))
        
        tk.Label(login_frame, text="Smart Food Ordering System", font=styles.SMALL_FONT, fg="#777", bg=styles.CARD_COLOR).pack(pady=(0, 30))
        
        # Form
        tk.Label(login_frame, text="Username", font=styles.SUBHEADER_FONT, bg=styles.CARD_COLOR, fg=styles.TEXT_COLOR).pack(anchor="w")
        self.username_entry = tk.Entry(login_frame, font=styles.NORMAL_FONT, width=30, bd=0, highlightbackground="#ccc", highlightthickness=1)
        self.username_entry.pack(pady=(5, 20), ipady=8)

        tk.Label(login_frame, text="Password", font=styles.SUBHEADER_FONT, bg=styles.CARD_COLOR, fg=styles.TEXT_COLOR).pack(anchor="w")
        self.password_entry = tk.Entry(login_frame, font=styles.NORMAL_FONT, width=30, bd=0, highlightbackground="#ccc", highlightthickness=1, show="*")
        self.password_entry.pack(pady=(5, 30), ipady=8)
        
        # Login Button
        login_btn = tk.Button(login_frame, text="Login", font=styles.SUBHEADER_FONT, bg=styles.PRIMARY_COLOR, fg="white", 
                              activebackground="#E64A19", activeforeground="white", bd=0, cursor="hand2", command=self.handle_login)
        login_btn.pack(fill="x", ipady=10, pady=(0, 15))

        # Register Link
        tk.Label(login_frame, text="Don't have an account?", font=styles.SMALL_FONT, bg=styles.CARD_COLOR, fg="#666").pack()
        register_link = tk.Button(login_frame, text="Create Account", font=(styles.SMALL_FONT[0], styles.SMALL_FONT[1], "underline"), 
                                  bg=styles.CARD_COLOR, fg=styles.PRIMARY_COLOR, bd=0, cursor="hand2", command=self.show_registration)
        register_link.pack()

    def handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        conn = get_conn()
        user = conn.execute("SELECT id, username, role FROM users WHERE lower(username) = lower(?) AND password = ?", (username, password)).fetchone()
        conn.close()
        
        if user:
            self.app.current_user = {"id": user[0], "username": user[1], "role": user[2]}
            messagebox.showinfo("Success", f"Welcome back, {username}!")
            self.app.show_main_dashboard()
        else:
            messagebox.showerror("Error", "Invalid username or password")

    def show_registration(self):
        self.app.clear_screen()
        
        reg_frame = tk.Frame(self.app.root, bg=styles.CARD_COLOR, padx=40, pady=40, highlightbackground="#ddd", highlightthickness=1)
        reg_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(reg_frame, text="Join QuickBite", font=("Segoe UI", 24, "bold"), fg=styles.PRIMARY_COLOR, bg=styles.CARD_COLOR).pack(pady=(0, 30))
        
        tk.Label(reg_frame, text="Username", font=styles.SUBHEADER_FONT, bg=styles.CARD_COLOR, fg=styles.TEXT_COLOR).pack(anchor="w")
        self.reg_user_entry = tk.Entry(reg_frame, font=styles.NORMAL_FONT, width=30, bd=0, highlightbackground="#ccc", highlightthickness=1)
        self.reg_user_entry.pack(pady=(5, 15), ipady=8)

        tk.Label(reg_frame, text="Password", font=styles.SUBHEADER_FONT, bg=styles.CARD_COLOR, fg=styles.TEXT_COLOR).pack(anchor="w")
        self.reg_pass_entry = tk.Entry(reg_frame, font=styles.NORMAL_FONT, width=30, bd=0, highlightbackground="#ccc", highlightthickness=1, show="*")
        self.reg_pass_entry.pack(pady=(5, 15), ipady=8)

        tk.Label(reg_frame, text="Confirm Password", font=styles.SUBHEADER_FONT, bg=styles.CARD_COLOR, fg=styles.TEXT_COLOR).pack(anchor="w")
        self.reg_confirm_entry = tk.Entry(reg_frame, font=styles.NORMAL_FONT, width=30, bd=0, highlightbackground="#ccc", highlightthickness=1, show="*")
        self.reg_confirm_entry.pack(pady=(5, 30), ipady=8)
        
        # Register Button
        reg_btn = tk.Button(reg_frame, text="Sign Up", font=styles.SUBHEADER_FONT, bg=styles.ACCENT_COLOR, fg="white", 
                            bd=0, cursor="hand2", command=self.handle_registration)
        reg_btn.pack(fill="x", ipady=10, pady=(0, 15))
        
        # Back to Login
        back_btn = tk.Button(reg_frame, text="Already have an account? Login", font=styles.SMALL_FONT, 
                             bg=styles.CARD_COLOR, fg="#666", bd=0, cursor="hand2", command=self.show_login)
        back_btn.pack()

    def handle_registration(self):
        username = self.reg_user_entry.get().strip()
        password = self.reg_pass_entry.get().strip()
        confirm = self.reg_confirm_entry.get().strip()
        
        if not username or not password:
            messagebox.showwarning("Incomplete", "Please fill all fields")
            return
            
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return
            
        conn = get_conn()
        
        existing = conn.execute("SELECT id FROM users WHERE lower(username) = lower(?)", (username,)).fetchone()
        if existing:
            conn.close()
            messagebox.showerror("Error", "Username already exists")
            return
            
        try:
            conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, 'user')", (username, password))
            conn.commit()
            messagebox.showinfo("Success", "Account created successfully! You can now login.")
            self.show_login()
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")
        finally:
            conn.close()
