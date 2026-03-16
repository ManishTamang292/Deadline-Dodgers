import sqlite3
from datetime import datetime


class DatabaseManager:

    def __init__(self):
        self.conn = sqlite3.connect("campus.db")
        self.cursor = self.conn.cursor()
        self._setup()
        self._seed_data()

    # ---------------- SETUP ----------------

    def _setup(self):

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id TEXT PRIMARY KEY,
            name TEXT,
            password_hash TEXT,
            points INTEGER DEFAULT 0,
            streak INTEGER DEFAULT 0,
            last_checkin TEXT,
            last_location TEXT
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS locations(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            points INTEGER
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS checkins(
            user_id TEXT,
            location_id INTEGER,
            timestamp TEXT
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS rewards(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            cost INTEGER
        )
        """)

        self.conn.commit()

    # ---------------- DEFAULT DATA ----------------

    def _seed_data(self):

        locations = [
            ("Harrison Library", 10),
            ("Campus Gym", 15),
            ("Student Union", 8),
            ("Sport Centre", 12)
            
        ]

        for name, pts in locations:
            self.add_location(name, pts)

        rewards = [
            ("Free Coffee", 50),
            ("Movie Ticket", 100),
            ("Campus Hoodie", 200),
            ("Exclusive Gym Pass", 500)
        ]

        for name, cost in rewards:
            self.add_reward(name, cost)

        # test user
        self.cursor.execute("""
        INSERT OR IGNORE INTO users(id,name,password_hash,points,streak)
        VALUES('student1','Test User','1234',100,2)
        """)

        self.conn.commit()

    # ---------------- USER ----------------

    def add_user(self, user, name, password):
        try:
            self.cursor.execute("""
            INSERT INTO users(id,name,password_hash)
            VALUES(?,?,?)
            """, (user, name, password))
            self.conn.commit()
            return True
        except:
            return False

    def get_user(self, user):
        self.cursor.execute("SELECT * FROM users WHERE id=?", (user,))
        return self.cursor.fetchone()

    def update_password(self, user, new):
        self.cursor.execute("""
        UPDATE users SET password_hash=? WHERE id=?
        """, (new, user))
        self.conn.commit()

    # ---------------- POINTS ----------------

    def add_points(self, user, pts):
        self.cursor.execute("""
        UPDATE users SET points = points + ? WHERE id=?
        """, (pts, user))
        self.conn.commit()

    def spend_points(self, user, pts):
        self.cursor.execute("""
        UPDATE users SET points = points - ? WHERE id=?
        """, (pts, user))
        self.conn.commit()

    def get_user_points(self, user):
        self.cursor.execute("SELECT points FROM users WHERE id=?", (user,))
        r = self.cursor.fetchone()
        return r[0] if r else 0

    # ---------------- STREAK ----------------

    def update_streak(self, user, streak, timestamp):

        self.cursor.execute("""
        UPDATE users
        SET streak=?, last_checkin=?
        WHERE id=?
        """, (streak, timestamp, user))

        self.conn.commit()

    def get_user_streak(self, user):
        self.cursor.execute("SELECT streak FROM users WHERE id=?", (user,))
        r = self.cursor.fetchone()
        return r[0] if r else 0

    def get_last_checkin(self, user):

        self.cursor.execute("""
        SELECT last_checkin FROM users WHERE id=?
        """, (user,))

        r = self.cursor.fetchone()

        return r[0] if r else None

    # ---------------- LEADERBOARD ----------------

    def get_leaderboard(self):

        self.cursor.execute("""
        SELECT id,name,points
        FROM users
        ORDER BY points DESC
        """)

        return self.cursor.fetchall()

    # ---------------- LOCATIONS ----------------

    def add_location(self, name, points):

        self.cursor.execute("""
        INSERT OR IGNORE INTO locations(name,points)
        VALUES(?,?)
        """, (name, points))

        self.conn.commit()

    def get_locations(self):

        self.cursor.execute("SELECT * FROM locations")

        return self.cursor.fetchall()

    # ---------------- REWARDS ----------------

    def add_reward(self, name, cost):

        self.cursor.execute("""
        INSERT OR IGNORE INTO rewards(name,cost)
        VALUES(?,?)
        """, (name, cost))

        self.conn.commit()

    def get_rewards(self):

        self.cursor.execute("SELECT * FROM rewards")

        return self.cursor.fetchall()

    # ---------------- CHECKIN ----------------

    def add_checkin(self, user, loc):

        self.cursor.execute("""
        INSERT INTO checkins(user_id,location_id,timestamp)
        VALUES(?,?,?)
        """, (user, loc, datetime.now().isoformat()))

        self.conn.commit()