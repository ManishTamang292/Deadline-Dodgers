from datetime import datetime, date


class CheckInService:

    def __init__(self, db):
        self.db = db

    def check_in(self, user, loc_id):

        today = date.today().isoformat()

        last = self.db.get_last_checkin(user)

        streak = self.db.get_user_streak(user)

        if last:

            last_date = last.split("T")[0]

            if last_date == today:
                return False, "Already checked in today", 0

            yesterday = date.fromisoformat(today).toordinal() - 1

            if date.fromisoformat(last_date).toordinal() == yesterday:
                streak += 1
            else:
                streak = 1

        else:
            streak = 1

        locs = self.db.get_locations()

        pts = next((l[2] for l in locs if l[0] == loc_id), 0)

        bonus = 5 if streak >= 3 else 0

        total = pts + bonus

        self.db.add_points(user, total)

        self.db.update_streak(user, streak, datetime.now().isoformat())

        self.db.add_checkin(user, loc_id)

        msg = f"+{pts} points"

        if bonus:
            msg += f" +{bonus} streak bonus 🔥"

        return True, msg, total