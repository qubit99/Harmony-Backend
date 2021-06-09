from datetime import datetime

from harmony import db


class UserAccount(db.Model):
    __tablename__ = "user_account"

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    public_id = db.Column(db.String(256), unique=True, nullable=False)
    f_name = db.Column(db.String(50))
    email = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.String(256))
    bio = db.Column(db.String)
    birth_date = db.Column(db.DateTime)
    job = db.Column(db.String)
    # preference_id = db.Column(db.Integer, db.ForeignKey('user_preference.id', ondelete='SET NULL'))
    sexual_orientation_id = db.Column(db.Integer, db.ForeignKey('sexual_orientation.id', ondelete='SET NULL'))
    gender = db.Column(db.String)
    ytmusic_link = db.Column(db.String)
    spotify_link = db.Column(db.String)
    lat = db.Column(db.Numeric)
    long = db.Column(db.Numeric)


class UserPreference(db.Model):
    __tablename__ = "user_preference"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_account.id', ondelete='SET NULL'))
    created = db.Column(db.DateTime, default=datetime.utcnow)
    modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    age_min = db.Column(db.Integer)
    age_max = db.Column(db.Integer)
    interested_gender = db.Column(db.String)
    distance = db.Column(db.Integer, default=4)


class SexualOrientation(db.Model):
    __tablename__ = "sexual_orientation"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)


class Passions(db.Model):
    __tablename__ = "passions"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)


class UserPassions(db.Model):
    __tablename__ = "user_passions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_account.id', ondelete='CASCADE'))
    passion_id = db.Column(db.Integer, db.ForeignKey('passions.id', ondelete='CASCADE'))


class UserImages(db.Model):
    __tablename__ = "user_images"

    img_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_account.id', ondelete='CASCADE'))
    img_ref = db.Column(db.String)
    img_src = db.Column(db.String)


class UserSwipes(db.Model):
    __tablename__ = "user_swipes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_account.id', ondelete='CASCADE'))
    swipe_ids = db.Column(db.ARRAY(db.String()), default=[])


class UserNotificationFeed(db.Model):
    __tablename__ = "user_notification_feed"

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    to_user_id = db.Column(db.String(256), db.ForeignKey('user_account.public_id', ondelete='CASCADE'))
    notification_type_id = db.Column(db.Integer, db.ForeignKey('notification_type.id', ondelete='CASCADE'))
    from_user_id = db.Column(db.String(256), db.ForeignKey('user_account.public_id', ondelete='CASCADE'))


class NotificationType(db.Model):
    """
    type 1: On getting a like
    type 2: On getting a message
    """
    __tablename__ = "notification_type"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    message = db.Column(db.String)


class UserMatches(db.Model):
    __tablename__ = "user_matches"

    id = db.Column(db.Integer, primary_key=True)
    user_id_1 = db.Column(db.String, db.ForeignKey('user_account.public_id', ondelete='CASCADE'))
    user_id_2 = db.Column(db.String, db.ForeignKey('user_account.public_id', ondelete='CASCADE'))
    created = db.Column(db.DateTime, default=datetime.utcnow)

