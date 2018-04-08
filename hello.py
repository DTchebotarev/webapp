from flask import Flask, request
app = Flask(__name__)

player_list = set()

current_player_id = 0

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/add_player/<player_id>')
def add_player(player_id):
    player_list.add(player_id)
    return "Ok"

@app.route('/list_players')
def list_players():
    return "\n".join(player_list)

@app.route('/set_player_form')
def player_form():
    return '''
        <head></head><body>
     <form action="/set_player">
      Player id:<br>
      <input type="text" name="id">
    </form>
    </body>
    '''

@app.route('/set_player')
def current_player():
    current_player_id = request.args.get('id')
    return "Set player id to {}".format(request.args.get('id'))
