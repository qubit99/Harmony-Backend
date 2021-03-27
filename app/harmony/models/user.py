from harmony import db, app

class UserAccount(db.Model):

    __tablename__ = "user_account"

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(256), unique = True)
    f_name = db.Column(db.String(50))
    email = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.String(256))
    




