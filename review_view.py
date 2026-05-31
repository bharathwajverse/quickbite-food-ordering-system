import tkinter as tk
from datetime import datetime
from db import get_conn
import styles

class ReviewView:
    def __init__(self, app):
        self.app = app

    def show(self):
        self.app.create_page_header("Customer Reviews")
        container = tk.Frame(self.app.content_area, bg=styles.BG_COLOR, padx=30)
        container.pack(fill="both", expand=True)
        
        # Submit Review Section
        submit_frame = tk.Frame(container, bg=styles.CARD_COLOR, pady=20, padx=20, highlightbackground="#eee", highlightthickness=1)
        submit_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(submit_frame, text="Write a Review", font=styles.SUBHEADER_FONT, bg=styles.CARD_COLOR).pack(anchor="w")
        
        tk.Label(submit_frame, text="Rating (1-5):", bg=styles.CARD_COLOR).pack(side="left", padx=(0, 10))
        self.rating_var = tk.StringVar(value="5")
        rating_spin = tk.Spinbox(submit_frame, from_=1, to=5, textvariable=self.rating_var, width=5)
        rating_spin.pack(side="left", padx=10)
        
        tk.Label(submit_frame, text="Comment:", bg=styles.CARD_COLOR).pack(side="left", padx=(20, 10))
        self.comment_entry = tk.Entry(submit_frame, width=40)
        self.comment_entry.pack(side="left", padx=10)
        
        submit_btn = tk.Button(submit_frame, text="Post Review", bg=styles.PRIMARY_COLOR, fg="white", bd=0, padx=15, 
                               command=self.submit_review)
        submit_btn.pack(side="left", padx=10)
        
        # List Reviews
        tk.Label(container, text="Recent Reviews", font=styles.SUBHEADER_FONT, bg=styles.BG_COLOR).pack(anchor="w", pady=10)
        
        reviews_list = tk.Frame(container, bg=styles.BG_COLOR)
        reviews_list.pack(fill="both", expand=True)
        
        conn = get_conn()
        reviews = conn.execute("SELECT comment, rating, review_date FROM reviews ORDER BY id DESC").fetchall()
        conn.close()
        
        for r in reviews:
            r_card = tk.Frame(reviews_list, bg=styles.CARD_COLOR, pady=10, padx=15, highlightbackground="#eee", highlightthickness=1)
            r_card.pack(fill="x", pady=5)
            tk.Label(r_card, text="★" * r[1], fg="#FFD700", bg=styles.CARD_COLOR, font=styles.SUBHEADER_FONT).pack(side="left")
            tk.Label(r_card, text=r[0], bg=styles.CARD_COLOR, font=styles.NORMAL_FONT).pack(side="left", padx=20)
            tk.Label(r_card, text=r[2], bg=styles.CARD_COLOR, font=styles.SMALL_FONT, fg="#999").pack(side="right")

    def submit_review(self):
        comment = self.comment_entry.get()
        rating = self.rating_var.get()
        if not comment: return
        
        date = datetime.now().strftime("%Y-%m-%d")
        conn = get_conn()
        conn.execute("INSERT INTO reviews (order_id, rating, comment, review_date) VALUES (?,?,?,?)",
                     ("GUI_TEST", rating, comment, date))
        conn.commit()
        conn.close()
        
        self.comment_entry.delete(0, 'end')
        self.show()
