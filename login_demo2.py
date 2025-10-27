import customtkinter as ctk
from tkinter import messagebox
import json, os, subprocess, sys
from utils import hash_password, verify_password

USER_FILE = "users.json"


def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    with open(USER_FILE, "r") as f:
        return json.load(f)


def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)


class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Personal Diary - Login")
        self.geometry("400x400")
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")

        self.users = load_users()
        self.active_frame = None
        self.show_login()

    def clear_frame(self):
        if self.active_frame:
            self.active_frame.destroy()

    def show_login(self):
        self.clear_frame()
        frame = ctk.CTkFrame(self)
        frame.pack(expand=True)

        ctk.CTkLabel(frame, text="Login", font=("Helvetica", 24, "bold")).pack(pady=20)
        username_entry = ctk.CTkEntry(frame, placeholder_text="Username")
        password_entry = ctk.CTkEntry(frame, placeholder_text="Password", show="*")
        username_entry.pack(pady=10)
        password_entry.pack(pady=10)

        def handle_login():
            username = username_entry.get()
            password = password_entry.get()
            if username not in self.users:
                messagebox.showerror("Error", "User not found.")
                return
            if verify_password(self.users[username]["password"], password):
                self.open_dashboard(username)
            else:
                messagebox.showerror("Error", "Invalid password.")

        ctk.CTkButton(frame, text="Login", command=handle_login).pack(pady=10)
        ctk.CTkButton(frame, text="Create Account", command=self.show_signup).pack(pady=10)
        self.active_frame = frame

    def show_signup(self):
        self.clear_frame()
        frame = ctk.CTkFrame(self)
        frame.pack(expand=True)

        ctk.CTkLabel(frame, text="Create Account", font=("Helvetica", 24, "bold")).pack(pady=20)
        username_entry = ctk.CTkEntry(frame, placeholder_text="Username")
        password_entry = ctk.CTkEntry(frame, placeholder_text="Password", show="*")
        username_entry.pack(pady=10)
        password_entry.pack(pady=10)

        def handle_signup():
            username = username_entry.get()
            password = password_entry.get()
            if username in self.users:
                messagebox.showerror("Error", "Username already exists.")
                return
            self.users[username] = {"password": hash_password(password)}
            save_users(self.users)
            messagebox.showinfo("Success", "Account created! Please log in.")
            self.show_login()

        ctk.CTkButton(frame, text="Sign Up", command=handle_signup).pack(pady=10)
        ctk.CTkButton(frame, text="Back to Login", command=self.show_login).pack(pady=10)
        self.active_frame = frame

    def open_dashboard(self, username):
        """Launch dashboard as a separate process."""
        self.destroy()
        subprocess.Popen([sys.executable, "dashboard.py", username])


if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()
