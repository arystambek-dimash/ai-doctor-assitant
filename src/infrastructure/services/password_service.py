import bcrypt


class PasswordService:
    def encrypt(self, password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def verify(self, password: str, db_password: str) -> bool:
        return bcrypt.checkpw(password=password.encode("utf-8"), hashed_password=db_password.encode("utf-8"))
