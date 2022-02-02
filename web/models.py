from web import db

'''members = db.Table('members',
    db.Column('member_id', db.Integer, db.ForeignKey('member.id'), primary_key=True),
    db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True)
)'''

class Book(db.Model):
    __tablename__ = 'book'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column(db.String(length=30), nullable=False, unique=True)
    author = db.Column(db.String(length=30), nullable=False)
    rent = db.Column(db.Integer(), nullable=False)
    quantity = db.Column(db.Integer(), nullable=False)
    members = db.relationship('Member', secondary='transaction')

    def __init__(self, name, author, rent, quantity):
        self.name = name
        self.author = author
        self.rent = rent
        self.quantity = quantity

class Member(db.Model):
    __tablename__ = 'member'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column(db.String(length=30), nullable=False)
    contact = db.Column(db.String(length=10), nullable=False, unique=True)
    debt = db.Column(db.Integer(), nullable=False, default=0)
    books = db.relationship('Book', secondary='transaction')

    def __init__(self, name, contact):
        self.name = name
        self.contact = contact

class Transaction(db.Model):
    __tablename__ = 'transaction'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    bookid = db.Column(db.Integer, db.ForeignKey('book.id', ondelete='CASCADE'))
    memberid = db.Column(db.Integer, db.ForeignKey('member.id', ondelete='CASCADE'))
    amount = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.TIMESTAMP, nullable=False)
    is_returned = db.Column(db.Boolean, default=False, nullable=False)

class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    username = db.Column(db.String(length=30), nullable=False)
    password = db.Column(db.String(length=30), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password
