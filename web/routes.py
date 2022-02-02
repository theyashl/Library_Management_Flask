from crypt import methods
from flask import render_template, request, url_for, redirect, session
from web import app, models, db
from datetime import datetime
import requests as rqs

@app.route('/')
@app.route('/home')
def home():
    books = models.Book.query.order_by(models.Book.id.desc()).limit(5).all()
    members = models.Member.query.order_by(models.Member.id.desc()).limit(5).all()
    transactions = models.Transaction.query.order_by(models.Transaction.id.desc()).limit(5).all()
    return render_template('index.html', items=books, persons=members, transactions=transactions)

@app.route('/books', methods=['GET', 'POST'])
def book():
    if request.method == 'POST':
        query = request.form['query']
        books = models.Book.query.filter(db.or_(models.Book.name.like('%'+query+'%'), models.Book.author.like('%'+query+'%'))).all()
    else:
        books = models.Book.query.all()
    return render_template('books.html', items=books)

@app.route('/members', methods=['GET', 'POST'])
def member():
    if request.method == 'POST':
        query = request.form['query']
        members = models.Member.query.filter(models.Member.name.like('%'+query+'%')).all()
    else:
        members = models.Member.query.all()
    return render_template('members.html', persons=members)

@app.route('/transactions', methods=['GET', 'POST'])
def transaction():
    if request.method == 'POST':
        tr = models.Transaction.query.filter_by(id=request.form['transactionId']).first()
        book = models.Book.query.filter_by(id=tr.bookid).first()
        book.quantity += 1
        user = models.Member.query.filter_by(id=tr.memberid).first()
        user.debt = user.debt + book.rent
        tr.is_returned = True
        db.session.commit()
    transactions = models.Transaction.query.all()
    return render_template('transactions.html', transactions=transactions)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if session.get("username") is None:
        return redirect(url_for('login'))
    book_id = request.args.get('book_id')
    book = models.Book.query.get(book_id)
    if request.method == 'POST':
        print("-------------\n\nREQUEST")
        print(request.form)
        user = models.Member.query.filter_by(contact=request.form['username']).first()
        if user is not None and (user.debt - book.rent) <= 500:
            book.quantity = book.quantity - 1
            transaction = models.Transaction(bookid=book.id, memberid=user.id, amount=book.rent, timestamp=datetime.now())
            db.session.add(transaction)
            db.session.commit()
            return render_template('success.html')
        else:
            return render_template('failed.html')
    else:
        return render_template('checkout.html', book=book)

@app.route('/edit/Book', methods=['GET', 'POST'])
def edit_book():
    if session.get("username") is None:
        return redirect(url_for('login'))
    book_id = request.args.get('book_id')
    if request.method == 'POST':
        if not book_id:
            book = models.Book(request.form['bookname'], request.form['author'], request.form['rent'], request.form['quantity'])
            db.session.add(book)
        else:
            book = models.Book.query.filter_by(id=book_id).first()
            book.name = request.form['bookname']
            book.author = request.form['author']
            book.rent = request.form['rent']
            book.quantity = request.form['quantity']
        db.session.commit()
        return redirect(url_for('book'))
    else:
        book = models.Book.query.filter_by(id=book_id).first()
        return render_template('editbook.html', book=book)

@app.route('/edit/Member', methods=['GET', 'POST'])
def edit_member():
    if session.get("username") is None:
        return redirect(url_for('login'))
    member_id = request.args.get('member_id')
    print(member_id)
    if request.method == 'POST':
        if not member_id:
            member = models.Member(request.form['membername'], request.form['contact'])
            db.session.add(member)
        else:
            member = models.Member.query.filter_by(id=member_id).first()
            member.name = request.form['membername']
            member.contact = request.form['contact']
            member.debt = request.form['debt']
        db.session.commit()
        return redirect(url_for('member'))
    else:
        member = models.Member.query.filter_by(id=member_id).first()
        return render_template('editmember.html', member=member)

@app.route('/delete/Book/<int:book_id>')
def delete_book(book_id):
    if session.get("username") is None:
        return redirect(url_for('login'))
    book = models.Book.query.filter_by(id=book_id).first()
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for('book'))

@app.route('/delete/Member/<int:member_id>')
def delete_member(member_id):
    if session.get("username") is None:
        return redirect(url_for('login'))
    member = models.Member.query.filter_by(id=member_id).first()
    db.session.delete(member)
    db.session.commit()
    return redirect(url_for('member'))

def sort_by_count(item):
    return -item[1]

@app.route('/report')
def report():
    books = models.Transaction.query.with_entities(models.Transaction.bookid, db.func.count(models.Transaction.id)).group_by(models.Transaction.bookid).limit(5).all()
    members = models.Transaction.query.with_entities(models.Transaction.memberid, db.func.sum(models.Transaction.amount)).group_by(models.Transaction.memberid).limit(5).all()
    books.sort(key=sort_by_count)
    members.sort(key=sort_by_count)
    itms = []
    prsn = []
    for book in books:
        itms.append((book[0], models.Book.query.filter_by(id=book[0]).first(), book[1]))
    for member in members:
        prsn.append((member[0], models.Member.query.filter_by(id=member[0]).first(), member[1]))
    del books
    del members
    return render_template('report.html', items=itms, persons=prsn)

@app.route('/import', methods=['GET', 'POST'])
def import_api():
    api_url = "https://api.itbook.store/1.0/search/{query}/{page}"
    if request.method == 'POST':
        query = request.form['query']
        total = int(request.form['total'])
        quantity = request.form['quantity']
        rent = request.form['rent']
        # query = "cpp"
        # total = 11
        books = []
        for i in range(1, (total//10)+2):
            books += (rqs.get(api_url.format(query=query, page=i)).json()['books'])
        for i in range(total):
            db.session.add(models.Book(books[i]['title'], "itbook", rent, quantity))
        db.session.commit()
        return render_template('success.html')
    else:
        return render_template('import.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = models.Admin.query.filter(db.and_(models.Admin.username==username, models.Admin.password ==password)).all()
        if admin:
            session["username"] = username
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error="Invalid Credentials!")
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    session["username"] = None
    return redirect(url_for('home'))