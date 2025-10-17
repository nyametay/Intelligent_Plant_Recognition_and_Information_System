from data import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = 'users'
    username = db.Column(db.String(50), primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    _password_hash = db.Column("password", db.String(128), nullable=False)
    profile_pic_data = db.Column(db.LargeBinary, nullable=True)
    profile_pic_mimetype = db.Column(db.String(50), nullable=True)
    images = db.relationship('Plant', backref='user', lazy=True)

    def to_dict(self):
        return {
            'username': self.username,
            'name': self.name,
            'email': self.email,
            'password': self._password_hash
        }

    @property
    def password(self):
        raise AttributeError("Password is write-only.")

    @password.setter
    def password(self, plain_text_password):
        self._password_hash = generate_password_hash(plain_text_password)

    def check_password(self, plain_text_password):
        return check_password_hash(self._password_hash, plain_text_password)


class Plant(db.Model):
    __tablename__: str = 'plants'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.String(255), nullable=False)
    image_data = db.Column(db.LargeBinary, nullable=False)
    plant_info = db.Column(db.JSON, nullable=False)
    plant_uses = db.Column(db.JSON, nullable=False)
    username = db.Column(db.String(50), db.ForeignKey('users.username'), nullable=False)


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    comment = db.Column(db.Text, nullable=False)
    rate = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(50), db.ForeignKey('users.username'), nullable=True)


# Helper function to get the count of a username
def get_user(username):
    return db.session.query(User).filter_by(username=username).first()


def get_plants(username):
    return db.session.query(Plant).filter_by(username=username).all()


def get_reviews():
    reviews = db.session.query(Comment).all()
    comments = []
    for review in reviews:
        user = get_user(review.username)
        if user:
            name = user.name
        else:
            name = 'Deleted User'
        comments.append({
            'id': review.id,
            'username': review.username,
            'rate': review.rate,
            'comment': review.comment,
            'name': name
        })
    return comments


def plants_saved_count(username):
    return db.session.query(Plant).filter_by(username=username).count()
