from flask import Flask, request, render_template, session, redirect, url_for, g
from functools import wraps
from os import urandom
import sqlite3

app = Flask(__name__)
users = {('Ivan','12345'):"Ivan", ('Boris','54321'):"Boris", ('Alexandr','qwerty'):"Alexandr"}
colors = ['red', 'green', 'blue', 'yellow', 'magenta']
app.secret_key = urandom(16)
DATABASE = 'databases/boxes.db'


def login_required(function_to_protect):
    @wraps(function_to_protect)
    def wrapper(*args, **kwargs):
        if 'user_id' in session:
            if session['user_id'] in users.values():
                return function_to_protect(*args, **kwargs)
            else:
                return redirect(url_for('login'))
        else:
            return redirect(url_for('login'))
    return wrapper

#---------------------------------------------------------------------------
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    with app.open_resource('databases/schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False, insert=False):
    db = get_db()
    cur = db.execute(query, args)
    if insert:
        db.commit()
        cur.close()
        return
    else:
        rv = cur.fetchall()
        cur.close()
        return (rv[0] if rv else None) if one else rv

def list_boxes():
    rows = query_db('SELECT name, color FROM boxes')
    return rows

def list_things(box):
    rows = query_db('SELECT thing, amount FROM things WHERE box=?', [box])
    return rows

#---------------------------------------------------------------------------
@app.route('/index')
@login_required
def index():
    return render_template('index.html', count=query_db('SELECT COUNT(*) FROM boxes', one=True)[0])

#---------------------------------------------------------------------------
@app.route('/boxes', methods=['GET','POST'])
@login_required
def method():
    if request.method == 'POST':
        return add_box()
    else:
        return get_boxes()

def add_box():
    color = request.args.get('color')
    if color == None:
        color = request.form.get('color')
    name = request.args.get('name')
    if name == None:
        name = request.form.get('name')
    response_text = ''

    boxes = list_boxes()
    if color in colors:
        if name in [box[0] for box in boxes] or color in [box[1] for box in boxes]:
            response_text = 'This box already exist'
        else:
            author = session['user_id']
            query_db('INSERT INTO boxes (name,color,author) VALUES (?,?,?)', (name, color, author), insert=True)
            response_text = 'Box created'
    else:
        response_text = 'This color does not exist'
    return render_template('boxes.html', cur_boxes=list_boxes(), text=response_text)

def get_boxes():
    return render_template('boxes.html', cur_boxes=list_boxes(), text='')

#---------------------------------------------------------------------------
@app.route('/boxes/<boxname>', methods=['GET','POST'])
@login_required
def box_method(boxname):
    box = query_db('SELECT * FROM boxes WHERE name=?', [boxname], one=True)
    if boxname != None:
        if request.method == 'POST':
            return add_thing(box)
        else:
            return get_things(box)
    else:
        return render_template('error.html', code='404', text='This box doesnt exist'), 404

def add_thing(box):
    if session['user_id'] == box[2]:
        name = request.args.get('name')
        if name == None:
            name = request.form.get('name')

        if query_db('SELECT * FROM things WHERE thing=? AND box=?', [name, box[0]], one=True) == None:
            query_db('INSERT INTO things (thing,amount,box) VALUES (?,?,?)', (name, str(1), box[0]), insert=True)
        else:
            query_db('UPDATE things SET amount=amount+1 WHERE thing=? AND box=?', [name, box[0]], insert=True)
        return render_template('box.html', name=box[0], box_color=box[1], box_things=list_things(box[0]), text='New thing added')
    else:
        return render_template('box.html', name=box[0], box_color=box[1], box_things=list_things(box[0]), text='You can\'t add things to that box')

def get_things(box):
    return render_template('box.html', name=box[0], box_color=box[1], box_things=list_things(box[0]), text='')

#--------------------------------------------------------------------------
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == "POST":
        user_name = request.form["name"]
        password = request.form["password"]

        if users.get((user_name,password))==None:
            return render_template('login.html', text='Invalid username or password')
        else:
            session['user_id'] = users.get((user_name,password))
            return redirect(url_for("index"))
    return render_template('login.html', text='')

#--------------------------------------------------------------------------
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))
    