from flask import Flask, request
import pandas as pd
app = Flask(__name__)

player_list = [5826, 5447, 5459, 4021, 4609, 4735, 5823, 4905, 4265, 4885]
bid_teams = {k:1000 for k in range(19)}
roster = set()

current_player_id = 0

player_df = pd.read_pickle('individual.pickle')

def get_info_on(player_id):
    return player_df.loc[player_id,['FirstName','LastName']].to_frame().to_html()

@app.route('/')
def root():
    return '''<html><head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head><body>
    UUuugh. Web is hard.<br>
    Click for data entry mode: <a href="/set_player_form">here</a><br>
    Click for bidding mode: <a href="/current_player_info">here</a><br>
    </body></html>
    '''

@app.route('/current_player_info')
def current_player_info():
    return '''<html><head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head><body>
    {}
    </body></html>
    '''.format(get_info_on(current_player_id))

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
        <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head><body>
     <form action="/set_player">
      Player id:<br>
      <input type="text" name="id"><br>
      <input type="submit" value="Submit">
    </form>
    </body>
    </html>
    '''

@app.route('/sold_to_form')
def sold_to_form():
    return '''
    <html>
        <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head><body>
     <form action="/sold_to">
      Player id:<br>
      Sold to:<br>
      <input type="text" name="buyer_team"><br>
      $ sold for:<br>
      <input type="text" name="sale amount"><br>
      <input type="submit" value="Submit">
    </form>
    </body>
    </html>
    '''

@app.route('/sold_to')
def sold_to():
    submitted_id = request.args.get('buyer_team')

    if submitted_id == 'us':
        global our_cash
        our_cash += -1*0
    try:
        submitted_id = int(submitted_id)
    except:
        submitted_id = '[not an integer: {}]'.format(submitted_id)
    if submitted_id not in player_df.index:
        return '''<html><head>
        <meta HTTP-EQUIV="REFRESH" content="2; url=/set_player_form">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head><body>
        You messed up. {} not a valid ID.<br>
        Redirecting you back to the submit page.<br>
        </body></html>'''.format(submitted_id)
    else:
        global current_player_id
        current_player_id = submitted_id
        first = player_df.loc[player_id,'FirstName']
        last = player_df.loc[player_id,'LastName']
        return '''
        <html>
        <head>
        <meta HTTP-EQUIV="REFRESH" content="2; url=/sold_to_form">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body>
        Set player id to {}, {} from {}.<br>
        Click <a href="/sold_to_form">here</a> if not redirected.
        </body>
        </html>
        '''.format(current_player_id, first+' '+last, player_df.loc[player_id,'team'])


@app.route('/set_player')
def current_player():
    submitted_id = request.args.get('id')
    try:
        submitted_id = int(submitted_id)
    except:
        submitted_id = '[not an integer: {}]'.format(submitted_id)
    if submitted_id not in player_df.index:
        return '''<html><head>
        <meta HTTP-EQUIV="REFRESH" content="2; url=/set_player_form">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head><body>
        You messed up. {} not a valid ID.<br>
        Redirecting you back to the submit page.<br>
        </body></html>'''.format(submitted_id)
    else:
        global current_player_id
        current_player_id = submitted_id
        first = player_df.loc[player_id,'FirstName']
        last = player_df.loc[player_id,'LastName']
        return '''
        <html>
        <head>
        <meta HTTP-EQUIV="REFRESH" content="2; url=/sold_to_form">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body>
        Set player id to {}, {} from {}.<br>
        Click <a href="/sold_to_form">here</a> if not redirected.
        </body>
        </html>
        '''.format(current_player_id, first+' '+last, player_df.loc[player_id,'team'])
