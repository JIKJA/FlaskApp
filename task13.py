from flask import Flask, request, render_template, session, redirect, url_for
from functools import wraps
from os import urandom

app = Flask(__name__)
colors = ['red', 'green', 'blue', 'yellow', 'magenta']
boxes = {}

#---------------------------------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html', count=len(boxes))

#---------------------------------------------------------------------------
@app.route('/boxes', methods=['GET','POST'])
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
            boxes[name] = (color, dict())
            response_text = 'Box created'
    else:
        response_text = 'This color does not exist'
    return render_template('boxes.html', cur_boxes=zip(boxes.keys(),[boxes.get(key)[0] for key in boxes.keys()]), text=response_text)

def get_boxes():
    return render_template('boxes.html', cur_boxes=zip(boxes.keys(),[boxes.get(key)[0] for key in boxes.keys()]), text='')

#---------------------------------------------------------------------------
@app.route('/boxes/<boxname>', methods=['GET','POST'])
def box_method(boxname):
    if boxname in boxes.keys():
        if request.method == 'POST':
            return add_thing(boxname)
        else:
            return get_things(boxname)
    else:
        return render_template('error.html', code='404', text='This box doesnt exist'), 404

def add_thing(boxname):
    name = request.args.get('name')
    if name == None:
        name = request.form.get('name')

    if boxes.get(boxname)[1].get(name) == None:
        boxes.get(boxname)[1][name] = 1
    else:
        boxes.get(boxname)[1][name] += 1
    return render_template('box.html', name=boxname, box=boxes.get(boxname), text='New thing added')

def get_things(boxname):
    return render_template('box.html', name=boxname, box=boxes.get(boxname), text='')

    