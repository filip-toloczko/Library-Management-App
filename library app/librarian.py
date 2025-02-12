import tkinter as tk
from tkinter import messagebox
import psycopg2
import librarian

def create_connection():
    try:
        conn = psycopg2.connect(
            host="127.0.0.1",
            database="project",
            user="postgres",
            password="Ariana1904",
            port="5432")
        return conn
    except psycopg2.DatabaseError as e:
        messagebox.showerror("Database Connection Error", e)
        return None


def exit_application(root):
    """ Handle the clean exit of the application. """
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()

def open_librarian_window():
    """ Open the librarian dashboard as a separate window. """
    root = tk.Tk()
    root.title("Librarian Dashboard")
    tk.Label(root, text="Welcome to the Librarian Dashboard").pack(pady=20)
    # Add more widgets or functionalities for the librarian
    root.protocol("WM_DELETE_WINDOW", lambda: exit_application(root))
    root.mainloop()
    
    
    librarian_window = tk.Toplevel()
    librarian_window.title("Librarian Dashboard")
    librarian_window.geometry('600x400')

    # Widgets for managing documents
    tk.Label(librarian_window, text="Manage Documents", font=('Arial', 16)).pack(pady=10)
    tk.Button(librarian_window, text="Add New Document", command=librarian.add_document).pack(pady=5)
    tk.Button(librarian_window, text="Update Document", command=librarian.update_document).pack(pady=5)
    tk.Button(librarian_window, text="Delete Document Copies", command=librarian.delete_document_copies).pack(pady=5)

    # Separator
    tk.Label(librarian_window, text="").pack(pady=10)  # Simple spacer

    # Widgets for managing clients
    tk.Label(librarian_window, text="Manage Clients", font=('Arial', 16)).pack(pady=10)
    tk.Button(librarian_window, text="Register New Client", command=librarian.register_client).pack(pady=5)
    tk.Button(librarian_window, text="Update Client Info", command=librarian.update_client_info).pack(pady=5)
    tk.Button(librarian_window, text="Delete Client", command=librarian.delete_client).pack(pady=5)

def add_book(barcode, copies, publisher, year, isbn, title, authors, edition, pages):
    """Add a new book, which includes adding entries in both Documents and NonJournal/Book tables."""
    conn = None
    try:
        conn = psycopg2.connect(
            host="127.0.0.1",
            database="project",
            user="postgres",
            password="Ariana1904",
            port="5432")
        cur = conn.cursor()
        # First, insert the document entry
        cur.execute(
            "INSERT INTO Documents (barcode, copies, publisher, year) VALUES (%s, %s, %s, %s)",
            (barcode, copies, publisher, year))
        # Then, insert the non-journal (since Book inherits from NonJournal)
        cur.execute(
            "INSERT INTO NonJournal (isbn, barcode) VALUES (%s, %s)",
            (isbn, barcode))
        # Finally, insert the book entry
        cur.execute(
            "INSERT INTO Book (isbn, title, authors, edition, pages) VALUES (%s, %s, %s, %s, %s)",
            (isbn, title, authors, edition, pages))
        conn.commit()
        messagebox.showinfo("Success", "Book added successfully")
    except psycopg2.DatabaseError as e:
        if conn:
            conn.rollback()
        messagebox.showerror("Database Error", f"Failed to add book: {str(e)}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

