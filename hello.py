from flask import Flask, request
app = Flask(__name__)

player_list = set()

current_player_id = 0

@app.route('/')
def hello_world():
    return '''
    UUuugh. Web is hard.

    '''

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
    <html>
        <head></head><body>
     <form action="/set_player">
      Player id:<br>
      <input type="text" name="id"><br>
      <input type="submit" value="Submit">
    </form>
    </body>
    </html>
    '''

@app.route('/sold_to_form')
def sold_to():


@app.route('/set_player')
def current_player():
    current_player_id = int(request.args.get('id'))
    return '''
    <html>
    <head>
    <meta HTTP-EQUIV="REFRESH" content="2; url=/sold_to_form">
    </head>
    <body>
    Set player id to {}, {} from {}.<br>
    Click <a href="/sold_to_form">here</a> if not redirected.
    </body>
    </html>
    '''.format(current_player_id, 'player_name','team_name')
