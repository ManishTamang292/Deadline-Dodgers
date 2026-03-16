import customtkinter as ctk
from tkinter import messagebox
from database import DatabaseManager
from auth_service import AuthService
from checkin_service import CheckInService

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

        bonus = 5
        self.db.add_points(self.current_user_id, bonus)

        messagebox.showinfo(
            "Daily Login Bonus",
            f"You received {bonus} points!"
        )

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
            ctk.CTkButton(sidebar, text=name,
                          width=180, command=cmd).pack(pady=6)

        ctk.CTkButton(
            sidebar,
            text="Logout",
            fg_color="red",
            command=self.build_login
        ).pack(pady=30)

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

        # ---- Stats Cards ----

        stats = [
            ("⭐ Points ", pts),
            ("🔥 Streak ", streak),
            ("🎮 Level ", level)
        ]

        stats_frame = ctk.CTkFrame(self.content)
        stats_frame.pack(pady=20)

        for i, (title, value) in enumerate(stats):

            card = ctk.CTkFrame(stats_frame, width=200, height=120)
            card.grid(row=0, column=i, padx=20)
            card.grid_propagate(False)

            ctk.CTkLabel(card, text=title).pack(pady=10)

            ctk.CTkLabel(
                card,
                text=value,
                font=ctk.CTkFont(size=28, weight="bold")
            ).pack()

        # ---- XP Progress ----

        xp_needed = 100
        progress = (pts % xp_needed) / xp_needed

        progress_frame = ctk.CTkFrame(self.content)
        progress_frame.pack(fill="x", pady=20)

        ctk.CTkLabel(
            progress_frame,
            text="XP Progress",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=10)

        bar = ctk.CTkProgressBar(progress_frame)
        bar.pack(fill="x", padx=20, pady=10)
        bar.set(progress)

        ctk.CTkLabel(
            progress_frame,
            text=f"{pts % xp_needed} / {xp_needed} XP to next level"
        ).pack()

        # ---- Facilities (2x2 Grid) ----

        ctk.CTkLabel(
            self.content,
            text="Campus Facilities",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(30, 10))

        facilities = [
            "📚 Harrison Library",
            "💬 Ask WLV",
            "🎓 Student Union",
            "🏋 Campus Gym"
        ]

        grid = ctk.CTkFrame(self.content)
        grid.pack()

        row = 0
        col = 0

        for fac in facilities:

            card = ctk.CTkFrame(grid, width=220, height=90)
            card.grid(row=row, column=col, padx=20, pady=15)
            card.grid_propagate(False)

            ctk.CTkLabel(card,
                         text=fac,
                         font=ctk.CTkFont(size=14)
                         ).pack(expand=True)

            col += 1
            if col > 1:
                col = 0
                row += 1

        # ---- Events ----

        ctk.CTkLabel(
            self.content,
            text="Upcoming Events",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(40, 10))

        events = [
            ("Open Evening", "27 May"),
            ("Postgraduate Day", "4 Jul"),
            ("Undergraduate Day", "4 Jul")
        ]

        for name, date in events:

            card = ctk.CTkFrame(self.content, height=70)
            card.pack(fill="x", padx=120, pady=8)
            card.pack_propagate(False)

            ctk.CTkLabel(
                card,
                text=name,
                font=ctk.CTkFont(size=15, weight="bold")
            ).pack(side="left", padx=20)

            ctk.CTkLabel(
                card,
                text=date
            ).pack(side="right", padx=20)

    # ---------------- OTHER PAGES ----------------

    def page_transport(self):

        self.clear_content()

        transport = [
            ("🚌 Bus Station", "5–7 minute walk from campus"),
            ("🚋 Metro", "7–8 minute walk from campus, tram access to Birmingham")
        ]

        for name, info in transport:

            card = ctk.CTkFrame(self.content)
            card.pack(fill="x", pady=10)

            ctk.CTkLabel(card, text=name).pack(anchor="w", padx=15)
            ctk.CTkLabel(card, text=info).pack(anchor="w", padx=15)

    def page_clubs(self):

        self.clear_content()

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

        leaderboard = self.db.get_leaderboard()

        medals = ["🥇", "🥈", "🥉"]

        for i, (user, name, pts) in enumerate(leaderboard):

            medal = medals[i] if i < 3 else "🏅"

            card = ctk.CTkFrame(self.content)
            card.pack(fill="x", pady=10)

            ctk.CTkLabel(
                card,
                text=f"{medal} {name} ({user})"
            ).pack(side="left", padx=15)

            ctk.CTkLabel(
                card,
                text=f"{pts} pts"
            ).pack(side="right", padx=15)


if __name__ == "__main__":
    app = LiveCampusHubApp()
    app.mainloop()