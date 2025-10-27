import customtkinter as ctk
from tkinter import messagebox, simpledialog, filedialog
from tkcalendar import Calendar
from fpdf import FPDF
import sys, json, os
from datetime import datetime
from utils import load_user_data, save_user_data, verify_password


class DiaryDashboard(ctk.CTk):
    def __init__(self, username):
        super().__init__()

        self.username = username
        self.title(f"Personal Diary - {username}")
        self.geometry("1000x600")

        # === Theme ===
        self.light_palette = {"bg": "#f5f0e6", "fg": "#333333", "accent": "#d9a76a"}
        self.dark_palette = {"bg": "#2c2c2c", "fg": "#f9d67a", "accent": "#fca311"}
        self.is_dark_mode = False

        ctk.set_appearance_mode("light")
        self.configure(fg_color=self.light_palette["bg"])

        # === Data ===
        self.data = load_user_data(username)
        self.selected_entry_index = None

        # === Layout ===
        self.create_sidebar()
        self.create_right_panel()
        self.refresh_entries()

    # ---------------------------------------------------
    # Sidebar (Calendar, Buttons)
    # ---------------------------------------------------
    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(self.sidebar, text="📅 Calendar", font=("Helvetica", 18, "bold")).pack(pady=10)
        self.calendar = Calendar(self.sidebar, selectmode="day")
        self.calendar.pack(pady=10)

        # Buttons
        buttons = [
            ("Add Entry", self.add_entry_popup),
            ("Edit Entry", self.edit_entry_popup),
            ("Delete Entry", self.delete_entry),
            ("Lock/Unlock", self.toggle_lock),
            ("Export as PDF", self.export_entry),
        ]
        for text, cmd in buttons:
            ctk.CTkButton(self.sidebar, text=text, command=cmd, width=200).pack(pady=5)

    # ---------------------------------------------------
    # Right Panel (Entries & Controls)
    # ---------------------------------------------------
    def create_right_panel(self):
        self.right_panel = ctk.CTkFrame(self, corner_radius=0)
        self.right_panel.pack(side="right", fill="both", expand=True)

        # Top Bar (Search, Refresh, Theme Toggle, Logout)
        top_bar = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        top_bar.pack(fill="x", pady=10)

        self.search_var = ctk.StringVar()
        ctk.CTkEntry(top_bar, textvariable=self.search_var, placeholder_text="Search by keyword or date (YYYY-MM-DD)", width=400).pack(side="top", pady=5)
        ctk.CTkButton(top_bar, text="Search", command=self.search_entries, width=80).pack(side="left", padx=10)
        ctk.CTkButton(top_bar, text="Refresh", command=self.refresh_entries, width=80).pack(side="left", padx=5)

        # Top Right Buttons
        ctk.CTkButton(top_bar, text="🌗 Toggle Theme", command=self.toggle_theme, width=120).pack(side="right", padx=10)
        ctk.CTkButton(top_bar, text="Logout", command=self.logout, fg_color="red").pack(side="right", padx=10)

        # Scrollable Entries Area
        self.entry_frame = ctk.CTkScrollableFrame(self.right_panel)
        self.entry_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # ---------------------------------------------------
    # Entry Cards
    # ---------------------------------------------------
    def refresh_entries(self, entries=None):
        """Refresh the entry display area."""
        for widget in self.entry_frame.winfo_children():
            widget.destroy()

        if entries is None:
            entries = self.data.get("entries", [])

        if not entries:
            ctk.CTkLabel(self.entry_frame, text="No entries yet.", font=("Helvetica", 14)).pack(pady=20)
            return

        for i, entry in enumerate(entries):
            card = ctk.CTkFrame(self.entry_frame, fg_color=self.get_theme_color("accent"), corner_radius=10)
            card.pack(fill="x", pady=5, padx=5)

            lock_icon = "🔒 " if entry.get("locked", False) else ""
            title = f"{lock_icon}{entry['title']}"

            ctk.CTkLabel(card, text=title, font=("Helvetica", 16, "bold"), anchor="w").pack(fill="x", padx=10, pady=5)

            if not entry.get("locked", False):
                content_box = ctk.CTkTextbox(card, height=80, wrap="word")
                content_box.insert("1.0", entry["content"])
                content_box.configure(state="disabled")
                content_box.pack(fill="x", padx=10, pady=(0, 10))
            else:
                ctk.CTkLabel(card, text="[Locked Entry – Unlock to view content]", text_color="gray").pack(pady=5)

            card.bind("<Button-1>", lambda e, idx=i: self.select_entry(idx))

    def select_entry(self, index):
        self.selected_entry_index = index

    # ---------------------------------------------------
    # Entry Management
    # ---------------------------------------------------
    def add_entry_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Add New Entry")
        popup.geometry("600x450")
        popup.grab_set()
        popup.focus_force()

        ctk.CTkLabel(popup, text="Title").pack(pady=5)
        title_entry = ctk.CTkEntry(popup, width=350)
        title_entry.pack(pady=5)

        ctk.CTkLabel(popup, text="Content").pack(pady=5)
        content_text = ctk.CTkTextbox(popup, width=350, height=200)
        content_text.pack(pady=5)

        def save_entry():
            new_entry = {
                "title": title_entry.get(),
                "content": content_text.get("1.0", "end").strip(),
                "date": self.calendar.get_date(),
                "locked": False
            }
            self.data["entries"].append(new_entry)
            save_user_data(self.username, self.data)
            self.refresh_entries()
            popup.destroy()
            messagebox.showinfo("Success", "Entry added successfully.")

        ctk.CTkButton(popup, text="Save", command=save_entry).pack(pady=10)

    def edit_entry_popup(self):
        if self.selected_entry_index is None:
            messagebox.showwarning("Warning", "Please select an entry to edit.")
            return

        entry = self.data["entries"][self.selected_entry_index]
        if entry.get("locked", False):
            messagebox.showwarning("Warning", "Unlock this entry before editing.")
            return

        popup = ctk.CTkToplevel(self)
        popup.title("Edit Entry")
        popup.geometry("400x400")
        popup.grab_set()
        popup.focus_force()

        ctk.CTkLabel(popup, text="Edit Title").pack(pady=5)
        title_entry = ctk.CTkEntry(popup, width=350)
        title_entry.insert(0, entry["title"])
        title_entry.pack(pady=5)

        ctk.CTkLabel(popup, text="Edit Content").pack(pady=5)
        content_text = ctk.CTkTextbox(popup, width=350, height=200)
        content_text.insert("1.0", entry["content"])
        content_text.pack(pady=5)

        def save_changes():
            entry["title"] = title_entry.get()
            entry["content"] = content_text.get("1.0", "end").strip()
            save_user_data(self.username, self.data)
            self.refresh_entries()
            popup.destroy()
            messagebox.showinfo("Success", "Changes saved successfully.")

        ctk.CTkButton(popup, text="Save Changes", command=save_changes).pack(pady=10)

    def delete_entry(self):
        if self.selected_entry_index is None:
            messagebox.showwarning("Warning", "Please select an entry to delete.")
            return

        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this entry?")
        if confirm:
            del self.data["entries"][self.selected_entry_index]
            save_user_data(self.username, self.data)
            self.refresh_entries()
            self.selected_entry_index = None

    # ---------------------------------------------------
    # Lock/Unlock Entry
    # ---------------------------------------------------
    def toggle_lock(self):
        if self.selected_entry_index is None:
            messagebox.showwarning("Warning", "Select an entry first.")
            return

        entry = self.data["entries"][self.selected_entry_index]
        if entry.get("locked", False):
            password = simpledialog.askstring("Unlock Entry", "Enter your password:", show="*")
            with open("users.json", "r") as f:
                users = json.load(f)
            if verify_password(users[self.username]["password"], password):
                entry["locked"] = False
                messagebox.showinfo("Unlocked", f"'{entry['title']}' unlocked successfully.")
            else:
                messagebox.showerror("Error", "Incorrect password.")
        else:
            entry["locked"] = True
            messagebox.showinfo("Locked", f"'{entry['title']}' locked successfully.")

        save_user_data(self.username, self.data)
        self.refresh_entries()

    # ---------------------------------------------------
    # Search & Export
    # ---------------------------------------------------
    def search_entries(self):
        keyword = self.search_var.get().lower().strip()
        if not keyword:
            self.refresh_entries()
            return

        filtered = [
            e for e in self.data["entries"]
            if keyword in e["title"].lower() or keyword in e["content"].lower() or keyword in e["date"].lower()
        ]
        self.refresh_entries(filtered)

    def export_entry(self):
        if self.selected_entry_index is None:
            messagebox.showwarning("Warning", "Select an entry to export.")
            return

        entry = self.data["entries"][self.selected_entry_index]
        if entry.get("locked", False):
            messagebox.showwarning("Warning", "Unlock entry before exporting.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not file_path:
            return

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, f"Title: {entry['title']}\nDate: {entry['date']}\n\n{entry['content']}")
        pdf.output(file_path)
        messagebox.showinfo("Success", f"Entry exported as PDF to {file_path}")

    # ---------------------------------------------------
    # Misc Utilities
    # ---------------------------------------------------
    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        theme = self.dark_palette if self.is_dark_mode else self.light_palette
        self.configure(fg_color=theme["bg"])
        ctk.set_appearance_mode("dark" if self.is_dark_mode else "light")
        self.refresh_entries()

    def get_theme_color(self, key):
        return self.dark_palette[key] if self.is_dark_mode else self.light_palette[key]

    def logout(self):
        self.destroy()
        os.system(f"{sys.executable} login.py")


# ----------------------------------------------
# Run Dashboard
# ----------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        messagebox.showerror("Error", "Username not provided.")
        sys.exit(1)
    username = sys.argv[1]
    app = DiaryDashboard(username)
    app.mainloop()
