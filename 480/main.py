import tkinter as tk
from tkinter import messagebox
import psycopg2
import librarian
import tkinter as tk


def show_frame(frame):
    frame.tkraise()

def create_connection():
    try:
        conn = psycopg2.connect(
            host="127.0.0.1",
            database="project_test",
            user="postgres",
            password="password",
            port="5432")
        return conn
    except psycopg2.DatabaseError as e:
        messagebox.showerror("Database Connection Error", e)
        return None


def open_client_window():
    """ Open the client window. """
    client_window = tk.Toplevel()
    client_window.title("Client Dashboard")
    tk.Label(client_window, text="Welcome, Client!").pack(pady=20)
    
    tk.Button(client_window, text="Open Account", command=open_account_window).pack(pady=10)
    tk.Button(client_window, text="Open Search", command=open_search_window).pack(pady=10)

def open_account_window():
    """ Open the account window. """
    account_window = tk.Toplevel()
    account_window.title("Account")
    tk.Label(account_window, text="Welcome to your Account!").pack(pady=20)

def open_search_window():
    """ Open the search window. """
    search_window = tk.Toplevel()
    search_window.title("Search")
    tk.Label(search_window, text="Search Interface").pack(pady=20)
    
    conn = create_connection()
    cur = conn.cursor()
    all_docs = """SELECT 
    d.barcode, d.year, d.publisher, d.copies,
    j.title AS journal_title, j.issue, j.name AS journal_name, j.authors, j.number,
    b.title AS book_title, b.authors AS book_authors, b.edition, b.pages,
    m.name AS magazine_name, m.month
    FROM documents d
    LEFT JOIN journal j ON d.barcode = j.barcode
    LEFT JOIN nonjournal n ON d.barcode = n.barcode
    LEFT JOIN book b ON n.isbn = b.isbn
    LEFT JOIN magazine m ON n.isbn = m.isbn;"""
    cur.execute(all_docs)
    rows = cur.fetchall()

def return_document():

    


def register():
    conn = create_connection()
    if conn is None:
        return
    
    role = registration_type.get()
    if role == "Librarian":
        add_librarian(conn, librarian_ssn.get(), librarian_name.get(), librarian_email.get(), librarian_password.get(), librarian_salary.get())
    else:
        add_member(conn, member_email.get(), member_password.get(), member_name.get(), member_card.get(), member_address.get())
    conn.close()

def add_librarian(conn, ssn, name, email, password, salary):
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO Librarians(ssn, name, email, password, salary) VALUES (%s, %s, %s, %s, %s)",
                    (ssn, name, email, password, salary))
        conn.commit()
        messagebox.showinfo("Success", "Librarian registered successfully")
    except psycopg2.IntegrityError:
        conn.rollback()
        messagebox.showerror("Error", "This email or SSN is already registered")
    finally:
        cur.close()

def add_member(conn, email, password, name, card_number, address):
    cur = conn.cursor()
    try:
        # Insert into Clients
        cur.execute("INSERT INTO Clients(email, name, password) VALUES (%s, %s, %s)",
                    (email, name, password))

        # Insert into ClientAddresses
        cur.execute("INSERT INTO ClientAddresses(email, address) VALUES (%s, %s)",
                    (email, address))

        # Insert into CreditCards
        cur.execute("INSERT INTO CreditCards(email, card_address, card_number) VALUES (%s, %s, %s)",
                    (email, address, card_number))

        # Commit all changes if all inserts are successful
        conn.commit()
        messagebox.showinfo("Success", "Member registered successfully")
    except psycopg2.IntegrityError as e:
        # Roll back transaction if any insert fails
        conn.rollback()
        if str(e).find("duplicate key value") != -1:
            messagebox.showerror("Error", "This email is already registered or the entered details are not unique.")
        else:
            messagebox.showerror("Error", "An error occurred while registering the member. Please check the input data.")
    except psycopg2.Error as e:
        # Handle other possible exceptions such as connection errors
        conn.rollback()
        messagebox.showerror("Database Error", f"An unexpected database error occurred: {str(e)}")
    finally:
        cur.close()


def login():
    """ Handle user login by checking both librarians and clients. """
    email = login_email.get()
    password = login_password.get()
    conn = create_connection()
    if conn is not None:
        cur = conn.cursor()
        # Try to log in as a librarian first
        cur.execute("SELECT password FROM Librarians WHERE email = %s", (email,))
        librarian_result = cur.fetchone()
        if librarian_result and librarian_result[0] == password:
            messagebox.showinfo("Login", "Login successful as Librarian")
            cur.close()
            conn.close()
            root.destroy()  # Destroy or hide the main login window
            librarian.open_librarian_window()  # Start the librarian's mainloop
            return
        # If not a librarian, try as a client
        cur.execute("SELECT password FROM Clients WHERE email = %s", (email,))
        client_result = cur.fetchone()
        if client_result and client_result[0] == password:
            messagebox.showinfo("Login", "Login successful as Client")
            open_client_window()
        else:
            messagebox.showerror("Login", "Invalid email or password")
        cur.close()
        conn.close()
        
        
        
# Main window setup
root = tk.Tk()
root.title("Library System")
root.geometry('800x600')

main_frame = tk.Frame(root)
main_frame.pack(fill='both', expand=True)

login_frame = tk.LabelFrame(root, text="Login")
login_frame.pack(fill='both', expand=True)

# Login form
tk.Label(login_frame, text="Email:").grid(row=0, column=0)
login_email = tk.Entry(login_frame)
login_email.grid(row=0, column=1)

tk.Label(login_frame, text="Password:").grid(row=1, column=0)
login_password = tk.Entry(login_frame, show='*')
login_password.grid(row=1, column=1)

tk.Button(login_frame, text="Login", command=lambda: [create_connection(), login()]).grid(row=2, columnspan=2)

# Registration type selection
registration_type = tk.StringVar(value="Member")
tk.Radiobutton(main_frame, text="Register as Member", variable=registration_type, value="Member", command=lambda: show_frame(member_frame)).pack()
tk.Radiobutton(main_frame, text="Register as Librarian", variable=registration_type, value="Librarian", command=lambda: show_frame(librarian_frame)).pack()

# Member registration form
member_frame = tk.LabelFrame(root, text="Member Registration")
member_frame.pack(fill='both', expand=True)

tk.Label(member_frame, text="Email:").grid(row=0, column=0)
member_email = tk.Entry(member_frame)
member_email.grid(row=0, column=1)

tk.Label(member_frame, text="Password:").grid(row=1, column=0)
member_password = tk.Entry(member_frame, show='*')
member_password.grid(row=1, column=1)

tk.Label(member_frame, text="Name:").grid(row=2, column=0)
member_name = tk.Entry(member_frame)
member_name.grid(row=2, column=1)

tk.Label(member_frame, text="Card Number:").grid(row=3, column=0)
member_card = tk.Entry(member_frame)
member_card.grid(row=3, column=1)

tk.Label(member_frame, text="Address:").grid(row=4, column=0)
member_address = tk.Entry(member_frame)
member_address.grid(row=4, column=1)

# Librarian registration form
librarian_frame = tk.LabelFrame(root, text="Librarian Registration")
librarian_frame.pack(fill='both', expand=True)

tk.Label(librarian_frame, text="SSN:").grid(row=0, column=0)
librarian_ssn = tk.Entry(librarian_frame)
librarian_ssn.grid(row=0, column=1)

tk.Label(librarian_frame, text="Name:").grid(row=1, column=0)
librarian_name = tk.Entry(librarian_frame)
librarian_name.grid(row=1, column=1)

tk.Label(librarian_frame, text="Email:").grid(row=2, column=0)
librarian_email = tk.Entry(librarian_frame)
librarian_email.grid(row=2, column=1)

tk.Label(librarian_frame, text="Password:").grid(row=3, column=0)
librarian_password = tk.Entry(librarian_frame, show='*')
librarian_password.grid(row=3, column=1)

tk.Label(librarian_frame, text="Salary:").grid(row=4, column=0)
librarian_salary = tk.Entry(librarian_frame)
librarian_salary.grid(row=4, column=1)

tk.Button(root, text="Register", command=register).pack(pady=20)



# Start with main menu
show_frame(main_frame)

root.mainloop()
