from flask import Flask
import os
app = Flask(__name__)

player_list = set()

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/add_player/<player_id>')
def add_player(player_id):
    player_list.add(player_id)

@app.route('/list_players'):
    return "\n".join(player_list)
