from flask import Flask, request, render_template, session, redirect, url_for
from functools import wraps
from os import urandom

app = Flask(__name__)
users = {('Ivan','12345'):"Ivan", ('Boris','54321'):"Boris", ('Alexandr','qwerty'):"Alexandr"}
colors = ['red', 'green', 'blue', 'yellow', 'magenta']
boxes = {}
app.secret_key = urandom(16)


def login_required(function_to_protect):
    @wraps(function_to_protect)
    def wrapper(*args, **kwargs):
        if 'user_id' in session:
            return function_to_protect(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrapper

#---------------------------------------------------------------------------
@app.route('/index')
@login_required
def index():
    return render_template('index.html', count=len(boxes))

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

    if color in colors:
        if name in boxes.keys() or color in [boxes.get(key)[0] for key in boxes.keys()]:
            response_text = 'This box already exist'
        else:
            author = session['user_id']
            boxes[name] = (color, author, dict())
            response_text = 'Box created'
    else:
        response_text = 'This color does not exist'
    return render_template('boxes.html', cur_boxes=zip(boxes.keys(),[boxes.get(key)[0] for key in boxes.keys()]), text=response_text)

def get_boxes():
    return render_template('boxes.html', cur_boxes=zip(boxes.keys(),[boxes.get(key)[0] for key in boxes.keys()]), text='')

#---------------------------------------------------------------------------
@app.route('/boxes/<boxname>', methods=['GET','POST'])
@login_required
def box_method(boxname):
    if boxname in boxes.keys():
        if request.method == 'POST':
            return add_thing(boxname)
        else:
            return get_things(boxname)
    else:
        return render_template('error.html', code='404', text='This box doesnt exist'), 404

def add_thing(boxname):
    if session['user_id'] == boxes[boxname][1]:
        name = request.args.get('name')
        if name == None:
            name = request.form.get('name')

        if boxes.get(boxname)[2].get(name) == None:
            boxes.get(boxname)[2][name] = 1
        else:
            boxes.get(boxname)[2][name] += 1
        return render_template('box.html', name=boxname, box_color=boxes.get(boxname)[0], box_things=boxes.get(boxname)[2], text='New thing added')
    else:
        return render_template('box.html', name=boxname, box_color=boxes.get(boxname)[0], box_things=boxes.get(boxname)[2], text='You can\'t add things to that box')

def get_things(boxname):
    return render_template('box.html', name=boxname, box_color=boxes.get(boxname)[0], box_things=boxes.get(boxname)[2], text='')

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
    