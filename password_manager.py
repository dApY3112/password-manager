import tkinter as tk
from tkinter import simpledialog, messagebox, ttk, filedialog
import string
import random
from crypto_utils import get_key, encrypt_password, decrypt_password
from db_utils import setup_db, store_password, retrieve_passwords, update_password, delete_password, backup_database, restore_database, check_password_expiry

def generate_strong_password():
    characters = string.ascii_letters + string.digits + "!@#$%^&*()"
    return ''.join(random.choice(characters) for i in range(12))

class PasswordManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Manager")
        self.root.geometry('600x300')  # Adjusted window size for better layout
        # Bind keyboard shortcuts
        self.root.bind('<Control-g>', lambda event: self.generate_password())
        self.root.bind('<Control-a>', lambda event: self.add_password())
        self.root.bind('<Control-l>', lambda event: self.show_passwords_window())
        self.root.bind('<Control-u>', lambda event: self.update_password_ui())
        self.root.bind('<Control-d>', lambda event: self.delete_password_ui())
        self.root.bind('<Control-b>', lambda event: backup_database())
        self.root.bind('<Control-r>', lambda event: self.restore_database_ui())

        self.high_contrast_mode = False
        # Setup the database
        setup_db()

        # Encryption Key
        self.key = get_key()

        # Create Widgets
        self.setup_widgets()
    def toggle_high_contrast(self):
            style = ttk.Style()
            if self.high_contrast_mode:
                # Switch to default theme
                style.configure('TButton', background='SystemButtonFace', foreground='SystemButtonText')
                style.configure('TEntry', background='SystemWindow', foreground='SystemWindowText', fieldbackground='SystemWindow')
                style.configure('TLabel', background='SystemWindow', foreground='SystemWindowText')
            else:
                # Switch to high contrast theme
                style.configure('TButton', background='black', foreground='white')
                style.configure('TEntry', background='black', foreground='white', fieldbackground='white')
                style.configure('TLabel', background='black', foreground='white')
            
            # Toggle the high contrast mode state
            self.high_contrast_mode = not self.high_contrast_mode
    def setup_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(sticky=(tk.E + tk.W + tk.N + tk.S))

        contrast_btn = tk.Button(main_frame, text="Toggle High Contrast", command=self.toggle_high_contrast)
        contrast_btn.grid(row=6, column=0, columnspan=2, pady=10)

        tk.Label(main_frame, text="Service:").grid(row=0, column=0, sticky='e')
        self.service_entry = tk.Entry(main_frame, width=50)
        self.service_entry.grid(row=0, column=1, padx=5, pady=5)
        self.service_entry.tooltip = "Enter the name of the service for which you want to manage passwords."

        tk.Label(main_frame, text="Username:").grid(row=1, column=0, sticky='e')
        self.username_entry = tk.Entry(main_frame, width=50)
        self.username_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(main_frame, text="Password:").grid(row=2, column=0, sticky='e')
        self.password_entry = tk.Entry(main_frame, show="*", width=50)
        self.password_entry.grid(row=2, column=1, padx=5, pady=5)

        generate_btn = tk.Button(main_frame, text="Generate Password", command=self.generate_password)
        generate_btn.grid(row=2, column=2, padx=5)

        add_btn = tk.Button(main_frame, text="Add", command=self.add_password)
        add_btn.grid(row=3, column=0, pady=10)

        list_btn = tk.Button(main_frame, text="List Passwords", command=self.show_passwords_window)
        list_btn.grid(row=3, column=1)

        update_btn = tk.Button(main_frame, text="Update", command=self.update_password_ui)
        update_btn.grid(row=4, column=0, pady=10)

        delete_btn = tk.Button(main_frame, text="Delete", command=self.delete_password_ui)
        delete_btn.grid(row=4, column=1)

        backup_btn = tk.Button(main_frame, text="Backup Database", command=backup_database)
        backup_btn.grid(row=5, column=0, pady=10)

        # For restore, you may want to use a file dialog to select a backup file
        restore_btn = tk.Button(main_frame, text="Restore Database", command=self.restore_database_ui)
        restore_btn.grid(row=5, column=1, pady=10)

        check_expiry_btn = tk.Button(main_frame, text="Check for Expired Passwords", command=self.check_password_expiry)
        check_expiry_btn.grid(row=7, column=0, columnspan=2, pady=10)
    def generate_password(self):
        new_password = generate_strong_password()
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, new_password)
        self.root.clipboard_clear()
        self.root.clipboard_append(new_password)
        self.root.after(15000, self.root.clipboard_clear)  # Clear clipboard after 15 seconds

    def add_password(self):
        service = self.service_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        if not service or not username or not password:
            messagebox.showerror("Error", "All fields are required!")
            return
        encrypted_password = encrypt_password(password, self.key)
        store_password(service, username, encrypted_password)
        messagebox.showinfo("Success", "Password added successfully!")
        self.service_entry.delete(0, tk.END)
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

    def show_passwords_window(self):
        window = tk.Toplevel(self.root)
        window.title("Stored Passwords")
        window.geometry("400x300")
        lb = tk.Listbox(window, width=50, height=15)
        lb.grid(row=0, column=0, padx=10, pady=10)
        scroll = tk.Scrollbar(window, orient="vertical", command=lb.yview)
        scroll.grid(row=0, column=1, sticky='ns')
        lb.configure(yscrollcommand=scroll.set)
        btn_frame = tk.Frame(window)
        btn_frame.grid(row=1, column=0, pady=10)
        copy_btn = tk.Button(btn_frame, text="Copy Password", command=lambda: self.copy_to_clipboard(lb))
        copy_btn.pack(side=tk.LEFT)
        close_btn = tk.Button(btn_frame, text="Close", command=window.destroy)
        close_btn.pack(side=tk.RIGHT)
        records = retrieve_passwords()
        for id, service, username, password in records:
            password_decrypted = decrypt_password(password, self.key)
            lb.insert(tk.END, f"{service} - {username} - {password_decrypted}")

    def copy_to_clipboard(self, listbox):
        try:
            index = listbox.curselection()[0]
            password = listbox.get(index).split(" - ")[2]
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            messagebox.showinfo("Clipboard", "Password copied to clipboard!")
        except IndexError:
            messagebox.showerror("Error", "No password selected!")

    def update_password_ui(self):
        record_id = simpledialog.askstring("Update Password", "Enter the ID of the password to update:")
        if record_id and record_id.isdigit():
            new_password = simpledialog.askstring("Update Password", "Enter the new password:")
            if new_password:
                new_encrypted_password = encrypt_password(new_password, self.key)
                update_password(int(record_id), new_encrypted_password)
                messagebox.showinfo("Success", "Password updated successfully!")
        else:
            messagebox.showerror("Error", "Invalid ID provided.")

    def delete_password_ui(self):
        record_id = simpledialog.askstring("Delete Password", "Enter the ID of the password to delete:")
        if record_id and record_id.isdigit():
            delete_password(int(record_id))
            messagebox.showinfo("Success", "Password deleted successfully!")
        else:
            messagebox.showerror("Error", "Invalid ID provided.")
    def restore_database_ui(self):
    # Use a file dialog to choose which backup to restore
        backup_path = filedialog.askopenfilename(title="Select Backup File", filetypes=[("Database files", "*.db")])
        if backup_path:
            restore_database(backup_path)
            messagebox.showinfo("Restore", "Database has been restored successfully.")
    def check_password_expiry(self):
        expired_services = check_password_expiry()
        if expired_services:
            messagebox.showwarning("Password Update Needed", f"The following services have passwords that need updating: {expired_services}")
        else:
            messagebox.showinfo("Password Check", "All passwords are up to date.")


# Main window
root = tk.Tk()
app = PasswordManagerGUI(root)
root.mainloop()
