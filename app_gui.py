import customtkinter as ctk
from tkinter import messagebox
from database import DatabaseManager
from auth_service import AuthService
from checkin_service import CheckInService
from datetime import date

PRIMARY = "#1f6aa5"
CARD = "#2b2b2b"
HOVER = "#3a3a3a"
ACCENT = "#4CAF50"
DANGER = "#e53935"
TEXT_GRAY = "#aaaaaa"

ctk.set_appearance_mode("white")
ctk.set_default_color_theme("blue")


class LiveCampusHubApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Live Campus Hub")
        self.geometry("1200x720")

        self.db = DatabaseManager()
        self.auth = AuthService(self.db)
        self.checkins = CheckInService(self.db)

        self.current_user_id = None

        self.build_login()

    # ---------------- UTIL ----------------

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    # ---------------- LEVEL SYSTEM ----------------

    def get_level(self, points):

        level = 1
        xp_needed = 100

        while points >= xp_needed:
            level += 1
            xp_needed += level * 100

        return level

    # ---------------- DAILY BONUS ----------------


    def daily_bonus(self):

        last = self.db.get_last_checkin(self.current_user_id)
        today = str(date.today())

        if last == today:
            return

        bonus = 5
        self.db.add_points(self.current_user_id, bonus)

        messagebox.showinfo(
        "Daily Login Bonus",
        f"You received {bonus} points!"
        )

    # update last login date
        self.db.update_streak(self.current_user_id,
                          self.db.get_user_streak(self.current_user_id),
                          today)

    # ---------------- LOGIN ----------------

    def build_login(self):

        self.clear()

        frame = ctk.CTkFrame(self)
        frame.pack(expand=True)

        ctk.CTkLabel(
            frame,
            text="Live Campus Hub",
            font=ctk.CTkFont(size=34, weight="bold")
        ).pack(pady=30)

        self.user_entry = ctk.CTkEntry(frame, width=260, placeholder_text="Student ID")
        self.user_entry.pack(pady=10)

        self.pass_entry = ctk.CTkEntry(frame, width=260, placeholder_text="Password", show="*")
        self.pass_entry.pack(pady=10)

        ctk.CTkButton(frame, text="Login", width=220,
                      command=self.do_login).pack(pady=10)

        ctk.CTkButton(frame, text="Create Account",
                      command=self.build_register).pack(pady=5)

        ctk.CTkButton(frame, text="Forgot Password",
                      command=self.forgot_password).pack()

    def do_login(self):

        user = self.user_entry.get()
        pw = self.pass_entry.get()

        ok, msg = self.auth.login(user, pw)

        if not ok:
            messagebox.showerror("Login Failed", msg)
            return

        self.current_user_id = user
        self.daily_bonus()
        self.build_dashboard()

    # ---------------- REGISTER ----------------

    def build_register(self):

        self.clear()

        frame = ctk.CTkFrame(self)
        frame.pack(expand=True)

        ctk.CTkLabel(frame,
                     text="Create Account",
                     font=ctk.CTkFont(size=28, weight="bold")
                     ).pack(pady=20)

        self.reg_user = ctk.CTkEntry(frame, placeholder_text="Student ID")
        self.reg_user.pack(pady=8)

        self.reg_name = ctk.CTkEntry(frame, placeholder_text="Full Name")
        self.reg_name.pack(pady=8)

        self.reg_pass = ctk.CTkEntry(frame, placeholder_text="Password", show="*")
        self.reg_pass.pack(pady=8)

        ctk.CTkButton(frame, text="Register",
                      command=self.register_user).pack(pady=15)

        ctk.CTkButton(frame, text="Back",
                      command=self.build_login).pack()

    def register_user(self):

        user = self.reg_user.get()
        name = self.reg_name.get()
        pw = self.reg_pass.get()

        ok, msg = self.auth.register(user, name, pw)

        if ok:
            messagebox.showinfo("Success", "Account created")
            self.build_login()
        else:
            messagebox.showerror("Error", msg)

    # ---------------- PASSWORD RESET ----------------

    def forgot_password(self):

        user = self.user_entry.get()

        if user == "":
            messagebox.showerror("Error", "Enter Student ID")
            return

        new_pw = ctk.CTkInputDialog(
            text="Enter new password",
            title="Reset Password"
        ).get_input()

        if new_pw:

            ok, msg = self.auth.reset_password(user, new_pw)

            if ok:
                messagebox.showinfo("Success", "Password updated")
            else:
                messagebox.showerror("Error", msg)

    # ---------------- DASHBOARD ----------------

    def build_dashboard(self):

        self.clear()

        sidebar = ctk.CTkFrame(self, width=220)
        sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(
            sidebar,
            text="LiveCampus",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=25)

        buttons = [
            ("🏠 Home", self.page_home),
            ("🚌 Transport", self.page_transport),
            ("👥 Clubs", self.page_clubs),
            ("🎁 Rewards", self.page_rewards),
            ("📍 Check-In", self.page_checkin),
            ("🏆 Leaderboard", self.page_leaderboard)
        ]

        for name, cmd in buttons:
            btn = ctk.CTkButton(
                sidebar,
                text=name,
                width=180,
                height=40,
                corner_radius=12,
                fg_color="#1f6aa5",
                hover_color=HOVER,
                command=cmd
            )
            btn.pack(fill="x", padx=10, pady=4)

        # --- USER PROFILE CARD ---

        profile_frame = ctk.CTkFrame(
            sidebar,
            corner_radius=12,
            fg_color="#2b2b2b"
        )
        profile_frame.pack(pady=20, padx=10, fill="x")

        ctk.CTkLabel(
            profile_frame,
            text="👤 User",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 0))

        ctk.CTkLabel(
            profile_frame,
            text=f"{self.current_user_id}",
            font=ctk.CTkFont(size=13),
            text_color="gray"
        ).pack(pady=(0, 10))

# --- LOGOUT BUTTON ---

        ctk.CTkButton(
            sidebar,
            text="Logout",
            fg_color="#e53935",
            hover_color="#b71c1c",
            corner_radius=10,
            height=40,
            command=self.build_login
        ).pack(pady=10, padx=10, fill="x")  

        main = ctk.CTkFrame(self)
        main.pack(side="right", fill="both", expand=True)

        self.content = ctk.CTkScrollableFrame(main)
        self.content.pack(fill="both", expand=True, padx=30, pady=30)

        self.page_home()

    # ---------------- HOME ----------------

    def page_home(self):

        self.clear_content()

        pts = self.db.get_user_points(self.current_user_id)
        streak = self.db.get_user_streak(self.current_user_id)
        level = self.get_level(pts)

        xp_needed = 100
        progress = (pts % xp_needed) / xp_needed

        dashboard = ctk.CTkFrame(self.content)
        dashboard.pack(fill="both", expand=True, padx=30, pady=20)

        dashboard.grid_columnconfigure(0, weight=1)
        dashboard.grid_columnconfigure(1, weight=1)

        dashboard.grid_rowconfigure(3, weight=1)
        dashboard.grid_rowconfigure(4, weight=1)

        header = ctk.CTkFrame(dashboard, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew")

        ctk.CTkLabel(
        header,
        text=f"Welcome back, {self.current_user_id} 👋",
        font=ctk.CTkFont(size=22, weight="bold")
        ).pack(side="left", padx=10)

    # ---------------- STATS ----------------

        stats_frame = ctk.CTkFrame(dashboard)
        stats_frame.grid(row=1, column=0, columnspan=2, pady=15)
        

        for i in range(3):
            stats_frame.grid_columnconfigure(i, weight=1)

        stats = [
            ("⭐ Points", pts),
            ("🔥 Streak", streak),
            ("🎮 Level", level)
        ]
        for i, (title, value) in enumerate(stats):

            card = ctk.CTkFrame(
                stats_frame,
                height=120,
                corner_radius=15,
                fg_color="#2b2b2b"
            )
            card.grid(row=0, column=i, padx=30, sticky="n")

            ctk.CTkLabel(card, text=title).pack(pady=(20,5))

            ctk.CTkLabel(
                card,
                text=value,
                font=ctk.CTkFont(size=28, weight="bold")
            ).pack()

    # ---------------- XP BAR ----------------

        progress_frame = ctk.CTkFrame(dashboard)
        progress_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)

        ctk.CTkLabel(
        progress_frame,
        text="XP Progress",
        font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=10)

        bar = ctk.CTkProgressBar(
        progress_frame,
        height=15,
        corner_radius=10
    )
        bar.pack(fill="x", padx=20, pady=10)
        bar.set(progress)

        ctk.CTkLabel(
        progress_frame,
        text=f"{pts % xp_needed} / {xp_needed} XP to next level"
        ).pack()

    # ---------------- LEFT COLUMN ----------------

        left_col = ctk.CTkFrame(dashboard)
        left_col.grid(
            row=3,
            column=0,
            columnspan=2,   # 🔥 THIS MAKES IT FULL WIDTH
            sticky="nsew",
            padx=20,
            pady=10
        )

        ctk.CTkLabel(
        left_col,
        text="🏫 Campus Facilities",
        font=ctk.CTkFont(size=25, weight="bold")
        ).pack(pady=10)

        facilities_frame = ctk.CTkFrame(left_col)
        facilities_frame.pack(fill="both", expand=True)

        for i in range(2):
            facilities_frame.grid_columnconfigure(i, weight=1)

        facilities = [
        "📚 Harrison Library",
        "💬 Ask WLV",
        "🎓 Student Union",
        "🏋 Campus Gym"
        ]

        for i, fac in enumerate(facilities):

            card = ctk.CTkFrame(facilities_frame, height=150)
            card.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="nsew")

            ctk.CTkLabel(
            card,
            text=fac,
            font=ctk.CTkFont(size=18, weight="bold")
            ).pack(expand=True, padx=10, pady=10)

    # ---------------- RIGHT COLUMN ----------------

        right_col = ctk.CTkFrame(dashboard)
        right_col.grid(
            row=4,          # 🔥 MOVE DOWN
            column=0,
            columnspan=2,   # 🔥 FULL WIDTH
            sticky="nsew",
            padx=20,
            pady=10
        )

        ctk.CTkLabel(
        right_col,
        text="📅 Upcoming Events",
        font=ctk.CTkFont(size=25, weight="bold")
        ).pack(pady=20)

        events = [
            ("Open Evening", "27 May"),
            ("Postgraduate Day", "4 Jul"),
            ("Undergraduate Day", "4 Jul")
        ]

        for event in events:

            card = ctk.CTkFrame(self.content, height=100)
            card.pack(fill="x", padx=120, pady=8)
            card.pack_propagate(False)

            ctk.CTkLabel(
            left_frame,
            text=event["title"],
            font=ctk.CTkFont(size=15, weight="bold")
            ).pack(anchor="w")

            ctk.CTkLabel(
            left_frame,
            text=event["location"],
            font=ctk.CTkFont(size=12)
            ).pack(anchor="w")

            ctk.CTkLabel(
            left_frame,
            text=event["description"],
            font=ctk.CTkFont(size=11)
            ).pack(anchor="w")

            ctk.CTkLabel(
            card,
            text=event["date"]
            ).pack(side="right", padx=20)


    # ---------------- OTHER PAGES ----------------

    def page_transport(self):

        self.clear_content()

        # Header
        ctk.CTkLabel(
        self.content,
        text="TRANSPORT 🚌",
        font=ctk.CTkFont(size=28, weight="bold")
        ).pack(pady=20)

        transport = [
            ("🚌 Bus Station", "5–7 minute walk from campus"),
            ("🚋 Metro", "7–8 minute walk from campus, tram access to Birmingham")
        ]

        for name, info in transport:

            btn = ctk.CTkButton(
            self.content,
            text=f"{name}\n{info}",
            height=80,
            command=lambda n=name: self.show_transport(n)
            )

            btn.pack(fill="x", pady=10)

    def show_transport(self, station):

        self.clear_content()

        # Title
        ctk.CTkLabel(
            self.content,
            text=station,
            font=ctk.CTkFont(size=25, weight="bold")
        ).pack(pady=20)

    # Data
        if "Bus" in station:
            services = [
                ("🟢 Bus-876", "Arrives in 2 min"),
                ("🟡 Bus-9", "Arrives in 6 min"),
                ("🟡 Bus-70", "Arrives in 12 min"),
                ("🔴 Bus-11", "Arrives in 18 min")
            ]

        elif "Metro" in station:
            services = [
                ("🚋 West Midlands Metro A", "Arrives in 3 min"),
                ("🚋 West Midlands Metro B", "Arrives in 9 min"),
                ("🚋 West Midlands Metro C", "Arrives in 15 min")
    ]

        # 🚶 WALK
        elif "Walk" in station:
            services = [
                ("🚶 Library Route", "5 min walk"),
                ("🚶 Gym Route", "7 min walk"),
                ("🚶 Student Union", "6 min walk"),
                ("🚶 Bus Stop", "4 min walk")
            ]

        # 🚕 CAB / TAXI
        elif "Cab" in station:
            services = [
                ("🚕 Uber", "Arrives in 3 min"),
                ("🚕 Bolt", "Arrives in 5 min"),
                ("🚕 Local Taxi", "Arrives in 7 min"),
                ("🚕 Premium Cab", "Arrives in 2 min")
            ]

        # 🚆 TRAIN
        elif "Train" in station:
            services = [
                ("🚆 Wolverhampton → Birmingham", "Departs in 10 min"),
                ("🚆 Wolverhampton → London", "Departs in 25 min"),
                ("🚆 Wolverhampton → Manchester", "Departs in 18 min"),
                ("🚆 Express Line", "Departs in 5 min")
            ]

        else:
            services = []

        # Cards
        for service, time in services:

            card = ctk.CTkFrame(self.content, fg_color="#2b2b2b")
            card.pack(fill="x", padx=20, pady=8)

            ctk.CTkLabel(
                card,
                text=service
            ).pack(side="left", padx=20, pady=10)

            ctk.CTkLabel(
                card,
                text=time
            ).pack(side="right", padx=20)

                # ✅ NOW OUTSIDE LOOP
        ctk.CTkButton(
            self.content,
            text="⬅ Back",
            width=200,
            height=40,
            corner_radius=12,
            command=self.page_transport
        ).pack(pady=30)

   # ---------------- CLUBS PAGE ----------------

    def page_clubs(self):
        self.clear_content()

        # Header
        ctk.CTkLabel(
        self.content,
        text="👥 CLUBS",
        font=ctk.CTkFont(size=28, weight="bold")
        ).pack(pady=20)

    # Grid container
        grid = ctk.CTkFrame(self.content, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=50)

        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)

        clubs = [
            "Law Society",
            "Business Society",
            "Chess Society",
            "Gaming Society"
        ]

        for s in clubs:

            card = ctk.CTkFrame(self.content)
            card.pack(fill="x", pady=10)

            ctk.CTkLabel(card, text=s).pack(padx=15)

    def page_rewards(self):

        self.clear_content()

         # Header
        ctk.CTkLabel(
        self.content,
        text="REWARDS 🎁",
        font=ctk.CTkFont(size=28, weight="bold")
        ).pack(pady=20)

        rewards = self.db.get_rewards()

        for r_id, name, cost in rewards:

            card = ctk.CTkFrame(self.content)
            card.pack(fill="x", pady=10)

            ctk.CTkLabel(card, text=name).pack(side="left", padx=15)
            ctk.CTkLabel(card, text=f"{cost} pts").pack(side="left")

            ctk.CTkButton(
                card,
                text="Redeem",
                command=lambda c=cost: self.redeem(c)
            ).pack(side="right", padx=20)

    def redeem(self, cost):

        pts = self.db.get_user_points(self.current_user_id)

        if pts < cost:
            messagebox.showerror("Error", "Not enough points")
            return

        self.db.spend_points(self.current_user_id, cost)

        messagebox.showinfo("Success", "Reward redeemed!")

        self.page_home()

    def page_checkin(self):

        self.clear_content()

        # Header
        ctk.CTkLabel(
        self.content,
        text="CHECK-IN ✅ ",
        font=ctk.CTkFont(size=28, weight="bold")
        ).pack(pady=20)

        locations = self.db.get_locations()

        for loc_id, name, pts in locations:

            card = ctk.CTkFrame(self.content)
            card.pack(fill="x", pady=10)

            ctk.CTkLabel(card, text=name).pack(side="left", padx=15)

            ctk.CTkButton(
                card,
                text=f"Check-In (+{pts})",
                command=lambda l=loc_id: self.do_checkin(l)
            ).pack(side="right", padx=20)

    def do_checkin(self, loc):

        ok, msg, _ = self.checkins.check_in(self.current_user_id, loc)

        messagebox.showinfo("Check-In", msg)

        self.page_home()

    def page_leaderboard(self):

        self.clear_content()

        # Header
        ctk.CTkLabel(
        self.content,
        text="🏆 LEADERBOARD",
        font=ctk.CTkFont(size=28, weight="bold")
        ).pack(pady=20)

        leaderboard = self.db.get_leaderboard()

        medals = ["🥇", "🥈", "🥉"]

        for i, (user, name, pts) in enumerate(leaderboard):

            medal = medals[i] if i < 3 else "🏅"

            card = ctk.CTkFrame(self.content)
            card.pack(fill="x", pady=10)

            ctk.CTkLabel(
                card,
                text=f"{medal} {name} ({user})"
            ).pack(side="left", padx=20)

            ctk.CTkLabel(
                card,
                text=f"{pts} pts"
            ).pack(side="right", padx=20)

if __name__ == "__main__":
    app = LiveCampusHubApp()
    app.mainloop()