import tkinter as tk
from tkinter import messagebox, ttk

from authentication import register_user, login_user
from database import connect_db
from generator import generate_records, save_records


# -----------------------------
# COLORS (dark monochrome theme)
# -----------------------------

BG_COLOR = "#0B0B0D"       # main window background
HEADER_BG = "#111114"      # dashboard header
CARD_BG = "#161619"        # cards / panels
INPUT_BG = "#1E1E22"       # text fields
BORDER = "#2C2C32"         # thin outlines
TEXT_COLOR = "#F2F2F3"     # main text
MUTED = "#8B8B94"          # secondary text
ACCENT = "#D9D9DE"         # links / highlights
BUTTON_DARK = "#0B0B0D"    # text on light buttons
WHITE = "#FFFFFF"


# -----------------------------
# GRADIENT BUTTON
# -----------------------------

class GradientButton(tk.Canvas):

    def __init__(
        self,
        parent,
        text,
        command,
        width=300,
        height=48
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
        self.text = text
        self.width = width
        self.height = height

        # silver gradient (normal) and brighter gradient (hover)
        self.normal_colors = ("#A8A8B0", "#E4E4E8")
        self.hover_colors = ("#C4C4CA", "#FFFFFF")

        self.draw_button(self.normal_colors)

        self.bind(
            "<Enter>",
            lambda event: self.draw_button(self.hover_colors)
        )

        self.bind(
            "<Leave>",
            lambda event: self.draw_button(self.normal_colors)
        )

        self.bind("<Button-1>", self.on_click)

    def draw_button(self, colors):

        self.delete("all")

        color1 = colors[0]
        color2 = colors[1]

        r1, g1, b1 = self.winfo_rgb(color1)
        r2, g2, b2 = self.winfo_rgb(color2)

        r1, g1, b1 = r1 // 256, g1 // 256, b1 // 256
        r2, g2, b2 = r2 // 256, g2 // 256, b2 // 256

        for x in range(self.width):
            ratio = x / max(self.width - 1, 1)

            red = int(r1 + (r2 - r1) * ratio)
            green = int(g1 + (g2 - g1) * ratio)
            blue = int(b1 + (b2 - b1) * ratio)

            color = f"#{red:02x}{green:02x}{blue:02x}"

            self.create_line(
                x, 0, x, self.height,
                fill=color
            )

        self.create_text(
            self.width // 2,
            self.height // 2,
            text=self.text,
            fill=BUTTON_DARK,
            font=("Arial", 11, "bold")
        )

    def on_click(self, event):

        if self.command:
            self.command()


# -----------------------------
# MAIN APPLICATION
# -----------------------------

class FakeDataGenApp:

    def __init__(self, root):

        self.root = root
        self.root.title("FakeDataGen")
        self.root.geometry("900x650")
        self.root.minsize(700, 550)
        self.root.configure(bg=BG_COLOR)
        self.current_user_id = None
        self.current_username = None

        self.create_login_screen()

    # -------------------------
    # HELPERS
    # -------------------------

    def style_entry(self, parent, show=""):

        return tk.Entry(
            parent,
            font=("Arial", 11),
            show=show,
            bg=INPUT_BG,
            fg=TEXT_COLOR,
            insertbackground=TEXT_COLOR,   # cursor color
            relief="flat",
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT
        )

    # -------------------------
    # SCREEN MANAGEMENT
    # -------------------------

    def clear_screen(self):

        for widget in self.root.winfo_children():
            widget.destroy()

    def create_card(self, height):

        card = tk.Frame(
            self.root,
            bg=CARD_BG,
            width=460,
            height=height,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        card.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

        card.pack_propagate(False)

        return card

    # -------------------------
    # LOGIN SCREEN
    # -------------------------

    def create_login_screen(self):

        self.clear_screen()

        card = self.create_card(490)

        tk.Label(
            card,
            text="FakeDataGen",
            font=("Arial", 27, "bold"),
            bg=CARD_BG,
            fg=WHITE
        ).pack(pady=(38, 5))

        tk.Label(
            card,
            text="CREATE  •  GENERATE  •  MANAGE",
            font=("Arial", 9, "bold"),
            bg=CARD_BG,
            fg=MUTED
        ).pack(pady=(0, 12))

        tk.Label(
            card,
            text="Welcome back!",
            font=("Arial", 17, "bold"),
            bg=CARD_BG,
            fg=TEXT_COLOR
        ).pack(pady=(5, 3))

        tk.Label(
            card,
            text="Sign in to continue to your account.",
            font=("Arial", 10),
            bg=CARD_BG,
            fg=MUTED
        ).pack(pady=(0, 25))

        form = tk.Frame(card, bg=CARD_BG)
        form.pack(fill="x", padx=55)

        tk.Label(
            form,
            text="Username or Email",
            font=("Arial", 10, "bold"),
            bg=CARD_BG,
            fg=TEXT_COLOR,
            anchor="w"
        ).pack(fill="x")

        self.username_entry = self.style_entry(form)

        self.username_entry.pack(
            fill="x",
            ipady=10,
            pady=(7, 18)
        )

        tk.Label(
            form,
            text="Password",
            font=("Arial", 10, "bold"),
            bg=CARD_BG,
            fg=TEXT_COLOR,
            anchor="w"
        ).pack(fill="x")

        self.password_entry = self.style_entry(form, show="*")

        self.password_entry.pack(
            fill="x",
            ipady=10,
            pady=(7, 22)
        )

        GradientButton(
            form,
            "LOGIN",
            self.login,
            width=350,
            height=48
        ).pack(fill="x")

        tk.Button(
            card,
            text="Create an account",
            font=("Arial", 10, "bold"),
            bg=CARD_BG,
            fg=ACCENT,
            activebackground=CARD_BG,
            activeforeground=WHITE,
            relief="flat",
            cursor="hand2",
            command=self.create_register_screen
        ).pack(pady=20)

        self.username_entry.focus_set()

        self.root.bind("<Return>", self.login_event)

    def login_event(self, event):

        self.login()

    # -------------------------
    # REGISTER SCREEN
    # -------------------------

    def create_register_screen(self):

        self.clear_screen()

        card = self.create_card(520)

        tk.Label(
            card,
            text="Create Account",
            font=("Arial", 25, "bold"),
            bg=CARD_BG,
            fg=WHITE
        ).pack(pady=(30, 5))

        tk.Label(
            card,
            text="Join FakeDataGen today.",
            font=("Arial", 10),
            bg=CARD_BG,
            fg=MUTED
        ).pack(pady=(0, 25))

        form = tk.Frame(card, bg=CARD_BG)
        form.pack(fill="x", padx=55)

        self.register_entries = {}

        fields = ["Username", "Email", "Password"]

        for field in fields:

            tk.Label(
                form,
                text=field,
                font=("Arial", 10, "bold"),
                bg=CARD_BG,
                fg=TEXT_COLOR,
                anchor="w"
            ).pack(fill="x")

            entry = self.style_entry(
                form,
                show="*" if field == "Password" else ""
            )

            entry.pack(
                fill="x",
                ipady=9,
                pady=(7, 15)
            )

            self.register_entries[field] = entry

        GradientButton(
            form,
            "CREATE ACCOUNT",
            self.register,
            width=350,
            height=48
        ).pack(fill="x", pady=(5, 5))

        tk.Button(
            card,
            text="Already have an account? Login",
            font=("Arial", 10),
            bg=CARD_BG,
            fg=ACCENT,
            activebackground=CARD_BG,
            activeforeground=WHITE,
            relief="flat",
            cursor="hand2",
            command=self.create_login_screen
        ).pack(pady=12)

    # -------------------------
    # DASHBOARD
    # -------------------------

    def create_dashboard(self, username):

        self.clear_screen()
        self.root.unbind("<Return>")

        header = tk.Frame(
            self.root,
            bg=HEADER_BG,
            height=100
        )

        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="FakeDataGen",
            font=("Arial", 23, "bold"),
            bg=HEADER_BG,
            fg=WHITE
        ).pack(side="left", padx=35, pady=25)

        tk.Label(
            header,
            text=f"Logged in as: {username}",
            font=("Arial", 10),
            bg=HEADER_BG,
            fg=MUTED
        ).pack(side="right", padx=35)

        # thin divider line under the header
        tk.Frame(
            self.root,
            bg=BORDER,
            height=1
        ).pack(fill="x")

        content = tk.Frame(
            self.root,
            bg=BG_COLOR
        )

        content.pack(
            fill="both",
            expand=True,
            padx=45,
            pady=35
        )

        tk.Label(
            content,
            text=f"Welcome back, {username}!",
            font=("Arial", 23, "bold"),
            bg=BG_COLOR,
            fg=WHITE
        ).pack(anchor="w")

        tk.Label(
            content,
            text="What would you like to do today?",
            font=("Arial", 11),
            bg=BG_COLOR,
            fg=MUTED
        ).pack(anchor="w", pady=(5, 30))

        cards = tk.Frame(content, bg=BG_COLOR)
        cards.pack(fill="x")

        self.create_dashboard_card(
            cards,
            "Generate Fake Data",
            "Create fictional user records.",
            "OPEN GENERATOR",
            self.open_generator
        ).pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 10)
        )

        self.create_dashboard_card(
            cards,
            "Saved Records",
            "View your generated records.",
            "VIEW RECORDS",
            self.open_records
        ).pack(
            side="left",
            fill="both",
            expand=True,
            padx=(10, 0)
        )

        tk.Button(
            content,
            text="LOG OUT",
            font=("Arial", 10, "bold"),
            bg=INPUT_BG,
            fg=TEXT_COLOR,
            activebackground=BORDER,
            activeforeground=WHITE,
            relief="flat",
            highlightthickness=1,
            highlightbackground=BORDER,
            cursor="hand2",
            command=self.logout
        ).pack(anchor="e", pady=35, ipadx=20, ipady=8)

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
            padx=20,
            pady=25
        )

        tk.Label(
            card,
            text=title,
            font=("Arial", 15, "bold"),
            bg=CARD_BG,
            fg=WHITE
        ).pack(anchor="w", pady=(0, 10))

        tk.Label(
            card,
            text=description,
            font=("Arial", 10),
            bg=CARD_BG,
            fg=MUTED
        ).pack(anchor="w", pady=(0, 25))

        GradientButton(
            card,
            button_text,
            command,
            width=260,
            height=43
        ).pack(fill="x")

        return card

    # -------------------------
    # GENERATOR PLACEHOLDER
    # -------------------------

    
def open_generator(self):

    self.clear_screen()

    header = tk.Frame(self.root, bg=HEADER_BG, height=85)
    header.pack(fill="x")
    header.pack_propagate(False)

    tk.Label(
        header,
        text="FakeDataGen",
        font=("Arial", 22, "bold"),
        bg=HEADER_BG,
        fg=WHITE
    ).pack(side="left", padx=30, pady=20)

    tk.Button(
        header,
        text="DASHBOARD",
        font=("Arial", 9, "bold"),
        bg=INPUT_BG,
        fg=TEXT_COLOR,
        relief="flat",
        cursor="hand2",
        command=lambda: self.create_dashboard(self.current_username)
    ).pack(side="right", padx=30)

    content = tk.Frame(self.root, bg=BG_COLOR)
    content.pack(fill="both", expand=True, padx=35, pady=25)

    tk.Label(
        content,
        text="Generate Fake Data",
        font=("Arial", 23, "bold"),
        bg=BG_COLOR,
        fg=WHITE
    ).pack(anchor="w")

    tk.Label(
        content,
        text="Create fictional user records using Faker.",
        font=("Arial", 10),
        bg=BG_COLOR,
        fg=MUTED
    ).pack(anchor="w", pady=(5, 20))

    panel = tk.Frame(
        content,
        bg=CARD_BG,
        padx=20,
        pady=18,
        highlightbackground=BORDER,
        highlightthickness=1
    )
    panel.pack(fill="x")

    tk.Label(
        panel,
        text="Number of Records",
        font=("Arial", 10, "bold"),
        bg=CARD_BG,
        fg=TEXT_COLOR
    ).pack(anchor="w")

    self.quantity_entry = self.style_entry(panel)
    self.quantity_entry.insert(0, "10")
    self.quantity_entry.pack(
        fill="x",
        ipady=9,
        pady=(8, 15)
    )

    GradientButton(
        panel,
        "GENERATE DATA",
        self.generate_data,
        width=300,
        height=45
    ).pack(fill="x")

    tk.Label(
        content,
        text="Generated Records",
        font=("Arial", 14, "bold"),
        bg=BG_COLOR,
        fg=WHITE
    ).pack(anchor="w", pady=(20, 10))

    table_frame = tk.Frame(content, bg=CARD_BG)
    table_frame.pack(fill="both", expand=True)

    columns = (
        "full_name",
        "email",
        "city",
        "country"
    )

    self.preview_table = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        height=9
    )

    headings = {
        "full_name": "Full Name",
        "email": "Email",
        "city": "City",
        "country": "Country"
    }

    for column in columns:
        self.preview_table.heading(
            column,
            text=headings[column]
        )
        self.preview_table.column(
            column,
            width=180,
            anchor="w"
        )

    scrollbar = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=self.preview_table.yview
    )

    self.preview_table.configure(
        yscrollcommand=scrollbar.set
    )

    self.preview_table.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar.pack(side="right", fill="y")

    self.generated_records = []

    self.save_button = tk.Button(
        content,
        text="SAVE RECORDS",
        font=("Arial", 10, "bold"),
        bg=ACCENT,
        fg=BUTTON_DARK,
        activebackground=WHITE,
        relief="flat",
        cursor="hand2",
        command=self.save_generated_records,
        state="disabled"
    )

    self.save_button.pack(
        anchor="e",
        pady=15,
        ipadx=20,
        ipady=8
    )


def generate_data(self):

    try:
        quantity = int(self.quantity_entry.get())

        if quantity < 10:
            messagebox.showwarning(
                "Invalid Quantity",
                "Please generate at least 10 records."
            )
            return

        records = generate_records(quantity)

        self.generated_records = records

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

        self.save_button.config(state="normal")

        messagebox.showinfo(
            "Generation Successful",
            f"{len(records)} fictional records generated!"
        )

    except ValueError:
        messagebox.showerror(
            "Invalid Input",
            "Please enter a valid whole number of at least 10."
        )

    except Exception as error:
        messagebox.showerror(
            "Generation Error",
            str(error)
        )


def save_generated_records(self):

    if not self.generated_records:
        messagebox.showwarning(
            "No Records",
            "Please generate records first."
        )
        return

    if self.current_user_id is None:
        messagebox.showerror(
            "Login Required",
            "Unable to identify the current user."
        )
        return

    try:
        saved_count = save_records(
            self.generated_records,
            self.current_user_id
        )

        messagebox.showinfo(
            "Saved Successfully",
            f"{saved_count} records saved to the database!"
        )

        self.save_button.config(state="disabled")

    except Exception as error:
        messagebox.showerror(
            "Save Error",
            str(error)
        )


    # -------------------------
    # RECORDS PLACEHOLDER
    # -------------------------

    def open_records(self):

        messagebox.showinfo(
            "Saved Records",
            "We will build the saved records screen next!"
        )

    # -------------------------
    # LOGOUT
    # -------------------------

    def logout(self):

        self.create_login_screen()

    # -------------------------
    # REGISTRATION FUNCTION
    # -------------------------

    def register(self):

        username = self.register_entries["Username"].get().strip()
        email = self.register_entries["Email"].get().strip()
        password = self.register_entries["Password"].get()

        success, message = register_user(
            username,
            email,
            password
        )

        if success:

            messagebox.showinfo(
                "Registration Successful",
                message
            )

            self.create_login_screen()

        else:

            messagebox.showerror(
                "Registration Failed",
                message
            )

    # -------------------------
    # LOGIN FUNCTION
    # -------------------------

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
                (username,))

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


# -----------------------------
# RUN APPLICATION
# -----------------------------

if __name__ == "__main__":

    root = tk.Tk()

    app = FakeDataGenApp(root)

    root.mainloop()