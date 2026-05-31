import sqlite3
import csv
import os
import tkinter as tk
from tkinter import filedialog, messagebox

def export_database():
    # Set up a hidden Tkinter root window
    root = tk.Tk()
    root.withdraw()
    
    # Ask the user to select a destination folder
    folder_path = filedialog.askdirectory(title="Select Folder to Save CSV Files")
    
    if not folder_path:
        print("Export cancelled by user.")
        return

    db_path = 'quickbite.db'
    if not os.path.exists(db_path):
        messagebox.showerror("Error", f"Database file '{db_path}' not found in the current folder.")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all table names from the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        exported_files = []
        for table_name_tuple in tables:
            table_name = table_name_tuple[0]
            
            # Skip SQLite internal tables
            if table_name.startswith('sqlite_'):
                continue
                
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            # Even if table is empty, we can export the headers
            headers = [description[0] for description in cursor.description]
            
            csv_file_path = os.path.join(folder_path, f"{table_name}_export.csv")
            
            with open(csv_file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(rows)
            
            exported_files.append(f"{table_name}_export.csv")
            print(f"Exported: {csv_file_path}")
        
        messagebox.showinfo("Export Successful", f"Successfully exported data to:\n{folder_path}\n\nFiles created:\n" + "\n".join(exported_files))
        
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during export:\n{str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    export_database()
