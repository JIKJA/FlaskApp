from flask import Flask, request
app = Flask(__name__)

users = []

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'POST':
        return add_user()
    else:
        return get_users()

def add_user():
    users.append(request.args.get('name'))
    return('User '+request.args.get('name')+' added')
def get_users():
    if len(users)==0:
        return('The room is full of people who care...')
    elif len(users)==1:
        return('There is '+users[0]+' in the room')
    else:
        return('There are '+ ", ".join(users)+ ' in the room')