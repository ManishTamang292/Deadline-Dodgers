class AuthService:

    def __init__(self, db):
        self.db = db

    def register(self, user, name, password):

        if self.db.get_user(user):
            return False, "User already exists"

        ok = self.db.add_user(user, name, password)

        if ok:
            return True, "Registration successful"

        return False, "Registration failed"

    def login(self, user, password):

        data = self.db.get_user(user)

        if not data:
            return False, "User not found"

        if data[2] != password:
            return False, "Wrong password"

        return True, "Login successful"

    def reset_password(self, user, new_password):

        if not self.db.get_user(user):
            return False, "User not found"

        self.db.update_password(user, new_password)

        return True, "Password updated"