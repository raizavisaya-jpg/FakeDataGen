
import tkinter as tk
from tkinter import messagebox, ttk

from authentication import register_user, login_user
from database import connect_db
from generator import generate_records, save_records


# -------------------------
# COLORS AND THEME
# -------------------------

BG_COLOR = "#0B0B0D"
HEADER_BG = "#111114"
CARD_BG = "#161619"
INPUT_BG = "#1E1E22"
BORDER = "#2C2C32"
TEXT_COLOR = "#F2F2F3"
MUTED = "#8B8B94"
ACCENT = "#D9D9DE"
BUTTON_DARK = "#0B0B0D"
WHITE = "#FFFFFF"


# -------------------------
# GRADIENT BUTTON
# -------------------------

class GradientButton(tk.Canvas):

    def __init__(
        self,
        parent,
        text,
        command,
        width=180,
        height=42
    ):
        super().__init__(
            parent,
            width=width,
            height=height,
            highlightthickness=0,
            bg=CARD_BG,
            cursor="hand2"
        )

        self.command = command

        start_color = (217, 217, 222)
        end_color = (139, 139, 148)

        for i in range(width):
            ratio = i / max(width - 1, 1)

            red = int(
                start_color[0] +
                (end_color[0] - start_color[0]) * ratio
            )

            green = int(
                start_color[1] +
                (end_color[1] - start_color[1]) * ratio
            )

            blue = int(
                start_color[2] +
                (end_color[2] - start_color[2]) * ratio
            )

            color = f"#{red:02x}{green:02x}{blue:02x}"

            self.create_line(
                i, 0, i, height,
                fill=color
            )

        self.create_text(
            width // 2,
            height // 2,
            text=text,
            fill=BUTTON_DARK,
            font=("Arial", 10, "bold")
        )

        self.bind(
            "<Button-1>",
            lambda event: self.command()
        )


# -------------------------
# MAIN APPLICATION
# -------------------------

class FakeDataGenApp:

    def __init__(self, root):
        self.root = root

        self.root.title("FakeDataGen")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        self.root.configure(bg=BG_COLOR)

        self.current_user_id = None
        self.current_username = None

        self.generated_records = []
        self.records_saved = False

        self.setup_treeview_style()
        self.create_login_screen()

    # -------------------------
    # GENERAL UI HELPERS
    # -------------------------

    def setup_treeview_style(self):

        style = ttk.Style()

        style.theme_use("clam")

        style.configure(
            "Treeview",
            background=INPUT_BG,
            foreground=TEXT_COLOR,
            fieldbackground=INPUT_BG,
            rowheight=30,
            borderwidth=0,
            font=("Arial", 9)
        )

        style.configure(
            "Treeview.Heading",
            background=HEADER_BG,
            foreground=TEXT_COLOR,
            font=("Arial", 9, "bold"),
            relief="flat"
        )

        style.map(
            "Treeview",
            background=[("selected", "#464858")],
            foreground=[("selected", WHITE)]
        )

    def clear_screen(self):

        for widget in self.root.winfo_children():
            widget.destroy()

    def create_card(self, parent, padding=25):

        return tk.Frame(
            parent,
            bg=CARD_BG,
            highlightbackground=BORDER,
            highlightthickness=1,
            padx=padding,
            pady=padding
        )

    def style_entry(self, parent, show=None):

        entry = tk.Entry(
            parent,
            bg=INPUT_BG,
            fg=TEXT_COLOR,
            insertbackground=WHITE,
            relief="flat",
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
            font=("Arial", 11),
            show=show
        )

        return entry

    def create_text_button(
        self,
        parent,
        text,
        command,
        color=TEXT_COLOR
    ):

        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=CARD_BG,
            fg=color,
            activebackground=CARD_BG,
            activeforeground=WHITE,
            relief="flat",
            cursor="hand2",
            font=("Arial", 10),
            borderwidth=0
        )

    # -------------------------
    # LOGIN SCREEN
    # -------------------------

    def create_login_screen(self):

        self.clear_screen()

        self.root.unbind("<Return>")

        container = tk.Frame(
            self.root,
            bg=BG_COLOR
        )
        container.pack(
            expand=True,
            fill="both"
        )

        card = self.create_card(
            container,
            padding=35
        )
        card.place(
            relx=0.5,
            rely=0.5,
            anchor="center",
            width=390
        )

        tk.Label(
            card,
            text="FakeDataGen",
            bg=CARD_BG,
            fg=TEXT_COLOR,
            font=("Arial", 25, "bold")
        ).pack(pady=(5, 8))

        tk.Label(
            card,
            text="Generate fictional data with ease.",
            bg=CARD_BG,
            fg=MUTED,
            font=("Arial", 10)
        ).pack(pady=(0, 30))

        tk.Label(
            card,
            text="Username or Email",
            bg=CARD_BG,
            fg=TEXT_COLOR,
            font=("Arial", 10)
        ).pack(anchor="w")

        self.username_entry = self.style_entry(card)
        self.username_entry.pack(
            fill="x",
            ipady=10,
            pady=(7, 18)
        )

        tk.Label(
            card,
            text="Password",
            bg=CARD_BG,
            fg=TEXT_COLOR,
            font=("Arial", 10)
        ).pack(anchor="w")

        self.password_entry = self.style_entry(
            card,
            show="*"
        )
        self.password_entry.pack(
            fill="x",
            ipady=10,
            pady=(7, 25)
        )

        GradientButton(
            card,
            "SIGN IN",
            self.login,
            width=310
        ).pack(pady=(0, 15))

        tk.Label(
            card,
            text="Don't have an account?",
            bg=CARD_BG,
            fg=MUTED,
            font=("Arial", 9)
        ).pack()

        self.create_text_button(
            card,
            "Create an account",
            self.create_register_screen,
            color=ACCENT
        ).pack(pady=(5, 0))

        self.root.bind(
            "<Return>",
            self.login_event
        )

    def login_event(self, event=None):
        self.login()

    # -------------------------
    # REGISTRATION SCREEN
    # -------------------------

    def create_register_screen(self):

        self.clear_screen()
        self.root.unbind("<Return>")

        container = tk.Frame(
            self.root,
            bg=BG_COLOR
        )
        container.pack(
            expand=True,
            fill="both"
        )

        card = self.create_card(
            container,
            padding=35
        )
        card.place(
            relx=0.5,
            rely=0.5,
            anchor="center",
            width=390
        )

        tk.Label(
            card,
            text="Create Account",
            bg=CARD_BG,
            fg=TEXT_COLOR,
            font=("Arial", 23, "bold")
        ).pack(pady=(5, 25))

        tk.Label(
            card,
            text="Username or Email",
            bg=CARD_BG,
            fg=TEXT_COLOR
        ).pack(anchor="w")

        self.reg_username = self.style_entry(card)
        self.reg_username.pack(
            fill="x",
            ipady=10,
            pady=(7, 15)
        )

        tk.Label(
            card,
            text="Email Address",
            bg=CARD_BG,
            fg=TEXT_COLOR
        ).pack(anchor="w")

        self.reg_email = self.style_entry(card)
        self.reg_email.pack(
            fill="x",
            ipady=10,
            pady=(7, 15)
        )

        tk.Label(
            card,
            text="Password",
            bg=CARD_BG,
            fg=TEXT_COLOR
        ).pack(anchor="w")

        self.reg_password = self.style_entry(
            card,
            show="*"
        )
        self.reg_password.pack(
            fill="x",
            ipady=10,
            pady=(7, 25)
        )

        GradientButton(
            card,
            "CREATE ACCOUNT",
            self.register,
            width=310
        ).pack(pady=(0, 15))

        self.create_text_button(
            card,
            "Back to Login",
            self.create_login_screen,
            color=ACCENT
        ).pack()

    # -------------------------
    # DASHBOARD
    # -------------------------

    def create_dashboard(self, username):

        self.clear_screen()
        self.root.unbind("<Return>")

        header = tk.Frame(
            self.root,
            bg=HEADER_BG,
            height=75
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="FakeDataGen",
            bg=HEADER_BG,
            fg=TEXT_COLOR,
            font=("Arial", 20, "bold")
        ).pack(
            side="left",
            padx=30
        )

        tk.Label(
            header,
            text=f"Welcome, {username}",
            bg=HEADER_BG,
            fg=MUTED,
            font=("Arial", 10)
        ).pack(
            side="right",
            padx=30
        )

        content = tk.Frame(
            self.root,
            bg=BG_COLOR
        )
        content.pack(
            expand=True,
            fill="both",
            padx=50,
            pady=45
        )

        tk.Label(
            content,
            text="Dashboard",
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            font=("Arial", 26, "bold")
        ).pack(anchor="w")

        tk.Label(
            content,
            text="Manage your fictional data records.",
            bg=BG_COLOR,
            fg=MUTED,
            font=("Arial", 10)
        ).pack(
            anchor="w",
            pady=(5, 35)
        )

        cards = tk.Frame(
            content,
            bg=BG_COLOR
        )
        cards.pack(fill="x")

        self.create_dashboard_card(
            cards,
            "Generate Fake Data",
            "Create and preview fictional records.",
            "OPEN GENERATOR",
            self.open_generator
        ).pack(
            side="left",
            expand=True,
            fill="both",
            padx=(0, 12)
        )

        self.create_dashboard_card(
            cards,
            "Saved Records",
            "View your previously saved records.",
            "VIEW RECORDS",
            self.open_records
        ).pack(
            side="left",
            expand=True,
            fill="both",
            padx=(12, 0)
        )

        self.create_text_button(
            content,
            "Log Out",
            self.logout,
            color=MUTED
        ).pack(
            anchor="w",
            pady=35
        )

    def create_dashboard_card(
        self,
        parent,
        title,
        description,
        button_text,
        command
    ):

        card = tk.Frame(
            parent,
            bg=CARD_BG,
            highlightbackground=BORDER,
            highlightthickness=1,
            padx=25,
            pady=30
        )

        tk.Label(
            card,
            text=title,
            bg=CARD_BG,
            fg=TEXT_COLOR,
            font=("Arial", 17, "bold")
        ).pack(anchor="w")

        tk.Label(
            card,
            text=description,
            bg=CARD_BG,
            fg=MUTED,
            font=("Arial", 10),
            wraplength=280,
            justify="left"
        ).pack(
            anchor="w",
            pady=(10, 25)
        )

        GradientButton(
            card,
            button_text,
            command,
            width=190
        ).pack(anchor="w")

        return card

    # -------------------------
    # GENERATOR SCREEN
    # -------------------------

    def open_generator(self):

        self.clear_screen()
        self.generated_records = []
        self.records_saved = False

        header = tk.Frame(
            self.root,
            bg=HEADER_BG,
            height=65
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Generate Fake Data",
            bg=HEADER_BG,
            fg=TEXT_COLOR,
            font=("Arial", 18, "bold")
        ).pack(
            side="left",
            padx=25
        )

        self.create_text_button(
            header,
            "Dashboard",
            lambda: self.create_dashboard(
                self.current_username
            )
        ).pack(
            side="right",
            padx=25
        )

        content = tk.Frame(
            self.root,
            bg=BG_COLOR
        )
        content.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=25
        )

        tk.Label(
            content,
            text="Generator Settings",
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            font=("Arial", 16, "bold")
        ).pack(anchor="w")

        settings = tk.Frame(
            content,
            bg=CARD_BG,
            padx=20,
            pady=18
        )
        settings.pack(
            fill="x",
            pady=(12, 20)
        )

        tk.Label(
            settings,
            text="Number of records (minimum 10):",
            bg=CARD_BG,
            fg=TEXT_COLOR,
            font=("Arial", 10)
        ).pack(side="left")

        self.quantity_entry = self.style_entry(settings)
        self.quantity_entry.insert(0, "10")
        self.quantity_entry.pack(
            side="left",
            padx=15,
            ipady=6,
            ipadx=8
        )

        GradientButton(
            settings,
            "GENERATE",
            self.generate_data,
            width=130
        ).pack(side="left")

        tk.Label(
            content,
            text="Generated Data Preview",
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            font=("Arial", 15, "bold")
        ).pack(anchor="w")

        table_frame = tk.Frame(
            content,
            bg=CARD_BG
        )
        table_frame.pack(
            fill="both",
            expand=True,
            pady=(12, 15)
        )

        columns = (
            "full_name",
            "email",
            "city",
            "country"
        )

        self.preview_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        self.preview_table.heading(
            "full_name",
            text="Full Name"
        )
        self.preview_table.heading(
            "email",
            text="Email"
        )
        self.preview_table.heading(
            "city",
            text="City"
        )
        self.preview_table.heading(
            "country",
            text="Country"
        )

        self.preview_table.column(
            "full_name",
            width=180
        )
        self.preview_table.column(
            "email",
            width=220
        )
        self.preview_table.column(
            "city",
            width=150
        )
        self.preview_table.column(
            "country",
            width=150
        )

        self.preview_table.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        bottom = tk.Frame(
            content,
            bg=BG_COLOR
        )
        bottom.pack(fill="x")

        self.save_button = GradientButton(
            bottom,
            "SAVE RECORDS",
            self.save_generated_records,
            width=160
        )
        self.save_button.pack(side="left")

        self.save_button.configure(
            state="disabled"
        )

        self.generator_status = tk.Label(
            bottom,
            text="Generate records to see the preview.",
            bg=BG_COLOR,
            fg=MUTED,
            font=("Arial", 9)
        )
        self.generator_status.pack(
            side="left",
            padx=18
        )

    def generate_data(self):

        try:
            quantity = int(
                self.quantity_entry.get().strip()
            )

            records = generate_records(quantity)

            self.generated_records = records
            self.records_saved = False

            for item in self.preview_table.get_children():
                self.preview_table.delete(item)

            for record in records:
                self.preview_table.insert(
                    "",
                    "end",
                    values=(
                        record["full_name"],
                        record["email"],
                        record["city"],
                        record["country"]
                    )
                )

            self.save_button.configure(
                state="normal"
            )

            self.generator_status.configure(
                text=f"{len(records)} records generated successfully."
            )

        except ValueError as error:
            messagebox.showwarning(
                "Invalid Quantity",
                str(error)
            )

        except Exception as error:
            messagebox.showerror(
                "Generation Error",
                f"Unable to generate records:\n{error}"
            )

    def save_generated_records(self):

        if not self.generated_records:
            messagebox.showwarning(
                "No Records",
                "Please generate records first."
            )
            return

        if self.records_saved:
            messagebox.showinfo(
                "Already Saved",
                "These records have already been saved."
            )
            return

        try:
            saved_count = save_records(
                self.generated_records,
                self.current_user_id
            )

            self.records_saved = True

            self.save_button.configure(
                state="disabled"
            )

            self.generator_status.configure(
                text=f"{saved_count} records saved successfully."
            )

            messagebox.showinfo(
                "Success",
                f"{saved_count} records saved successfully!"
            )

        except Exception as error:
            messagebox.showerror(
                "Save Error",
                f"Unable to save records:\n{error}"
            )

    # -------------------------
    # SAVED RECORDS SCREEN
    # -------------------------

    def open_records(self):

        self.clear_screen()

        header = tk.Frame(
            self.root,
            bg=HEADER_BG,
            height=65
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Saved Records",
            bg=HEADER_BG,
            fg=TEXT_COLOR,
            font=("Arial", 18, "bold")
        ).pack(
            side="left",
            padx=25
        )

        self.create_text_button(
            header,
            "Dashboard",
            lambda: self.create_dashboard(
                self.current_username
            )
        ).pack(
            side="right",
            padx=25
        )

        content = tk.Frame(
            self.root,
            bg=BG_COLOR
        )
        content.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=25
        )

        tk.Label(
            content,
            text="Your Generated Records",
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            font=("Arial", 20, "bold")
        ).pack(anchor="w")

        tk.Label(
            content,
            text="Only records saved under your account are displayed.",
            bg=BG_COLOR,
            fg=MUTED,
            font=("Arial", 10)
        ).pack(
            anchor="w",
            pady=(5, 18)
        )

        search_frame = tk.Frame(
            content,
            bg=BG_COLOR
        )
        search_frame.pack(
            fill="x",
            pady=(0, 15)
        )

        self.search_entry = self.style_entry(
            search_frame
        )
        self.search_entry.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=8
        )

        self.search_entry.insert(
            0,
            "Search by name or email"
        )

        tk.Button(
            search_frame,
            text="SEARCH",
            command=self.search_saved_records,
            bg=INPUT_BG,
            fg=TEXT_COLOR,
            activebackground=BORDER,
            activeforeground=WHITE,
            relief="flat",
            padx=15,
            pady=8,
            cursor="hand2"
        ).pack(
            side="left",
            padx=(10, 0)
        )

        columns = (
            "id",
            "full_name",
            "email",
            "city",
            "country",
            "created_at"
        )

        table_frame = tk.Frame(
            content,
            bg=CARD_BG
        )
        table_frame.pack(
            fill="both",
            expand=True
        )

        self.records_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        headings = {
            "id": "ID",
            "full_name": "Full Name",
            "email": "Email",
            "city": "City",
            "country": "Country",
            "created_at": "Date Saved"
        }

        widths = {
            "id": 45,
            "full_name": 160,
            "email": 190,
            "city": 120,
            "country": 120,
            "created_at": 150
        }

        for column in columns:
            self.records_table.heading(
                column,
                text=headings[column]
            )
            self.records_table.column(
                column,
                width=widths[column],
                minwidth=45
            )

        vertical_scroll = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.records_table.yview
        )

        self.records_table.configure(
            yscrollcommand=vertical_scroll.set
        )

        self.records_table.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(10, 0),
            pady=10
        )

        vertical_scroll.pack(
            side="right",
            fill="y",
            pady=10,
            padx=(0, 10)
        )

        actions = tk.Frame(
            content,
            bg=BG_COLOR
        )
        actions.pack(
            fill="x",
            pady=(15, 0)
        )

        tk.Button(
            actions,
            text="REFRESH",
            command=self.load_saved_records,
            bg=INPUT_BG,
            fg=TEXT_COLOR,
            activebackground=BORDER,
            activeforeground=WHITE,
            relief="flat",
            padx=18,
            pady=9,
            cursor="hand2"
        ).pack(side="left")

        tk.Button(
            actions,
            text="DELETE SELECTED",
            command=self.delete_selected_record,
            bg=INPUT_BG,
            fg=TEXT_COLOR,
            activebackground=BORDER,
            activeforeground=WHITE,
            relief="flat",
            padx=18,
            pady=9,
            cursor="hand2"
        ).pack(
            side="left",
            padx=10
        )

        self.records_status = tk.Label(
            actions,
            text="",
            bg=BG_COLOR,
            fg=MUTED,
            font=("Arial", 9)
        )
        self.records_status.pack(
            side="right"
        )

        self.load_saved_records()

    def load_saved_records(self, search_term=""):

        for item in self.records_table.get_children():
            self.records_table.delete(item)

        connection = connect_db()
        cursor = connection.cursor()

        if search_term:
            cursor.execute("""
                SELECT
                    id,
                    full_name,
                    email,
                    city,
                    country,
                    created_at
                FROM generated_data
                WHERE user_id = ?
                AND (
                    full_name LIKE ?
                    OR email LIKE ?
                )
                ORDER BY id DESC
            """, (
                self.current_user_id,
                f"%{search_term}%",
                f"%{search_term}%"
            ))

        else:
            cursor.execute("""
                SELECT
                    id,
                    full_name,
                    email,
                    city,
                    country,
                    created_at
                FROM generated_data
                WHERE user_id = ?
                ORDER BY id DESC
            """, (self.current_user_id,))

        records = cursor.fetchall()
        connection.close()

        for record in records:
            self.records_table.insert(
                "",
                "end",
                values=record
            )

        self.records_status.configure(
            text=f"{len(records)} record(s) found."
        )

    def search_saved_records(self):

        search_term = self.search_entry.get().strip()

        if search_term == "Search by name or email":
            search_term = ""

        self.load_saved_records(search_term)

    def delete_selected_record(self):

        selected = self.records_table.selection()

        if not selected:
            messagebox.showwarning(
                "No Selection",
                "Please select a record to delete."
            )
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete the selected record?"
        )

        if not confirm:
            return

        selected_item = self.records_table.item(
            selected[0]
        )

        record_id = selected_item["values"][0]

        connection = connect_db()
        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM generated_data
            WHERE id = ? AND user_id = ?
        """, (
            record_id,
            self.current_user_id
        ))

        connection.commit()
        connection.close()

        self.load_saved_records()

        messagebox.showinfo(
            "Deleted",
            "Record deleted successfully."
        )

    # -------------------------
    # REGISTRATION AND LOGIN
    # -------------------------

    def register(self):

        username = self.reg_username.get().strip()
        email = self.reg_email.get().strip()
        password = self.reg_password.get()

        success, message = register_user(
            username,
            email,
            password
        )

        if success:
            messagebox.showinfo(
                "Registration",
                message
            )
            self.create_login_screen()

        else:
            messagebox.showerror(
                "Registration Error",
                message
            )

    def login(self):

        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showwarning(
                "Missing Information",
                "Please enter your username and password."
            )
            return

        success, message = login_user(
            username,
            password
        )

        if success:

            connection = connect_db()
            cursor = connection.cursor()

            cursor.execute(
                "SELECT id FROM users WHERE username = ?",
                (username,)
            )

            user = cursor.fetchone()
            connection.close()

            if user:
                self.current_user_id = user[0]
                self.current_username = username

                self.create_dashboard(username)

            else:
                messagebox.showerror(
                    "Login Error",
                    "Unable to retrieve your user account."
                )

        else:
            messagebox.showerror(
                "Login Failed",
                message
            )

    # -------------------------
    # LOGOUT
    # -------------------------

    def logout(self):

        self.current_user_id = None
        self.current_username = None

        self.generated_records = []
        self.records_saved = False

        self.create_login_screen()


# -------------------------
# RUN APPLICATION
# -------------------------

if __name__ == "__main__":

    root = tk.Tk()

    app = FakeDataGenApp(root)

    root.mainloop()
