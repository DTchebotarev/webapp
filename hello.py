from flask import Flask, request
from multiprocessing import Pool
from random import random
import pandas as pd
from functools import lru_cache
app = Flask(__name__)


player_df = pd.read_pickle('individual.pickle')
player_list = list(player_df.index)

bid_teams = {k:1000 for k in range(17)}
our_id = 0
roster = set()
elo_scores = pd.read_html('http://morehockeystats.com/teams/elo?inline=1&season=2017&page=1&hl=',index_col=0,header=0)[0]
team_mapping = {'ANA':'Anaheim Ducks', 'ARI':'Arizona Coyotes', 'BOS':'Boston Bruins',
'BUF':'Buffalo Sabres','CGY':'Calgary Flames', 'CAR':'Carolina Hurricanes',
'CHI':'Chicago Blackhawks', 'COL':'Colorado Avalanche','CBJ':'Columbus Blue Jackets',
'DAL':'Dallas Stars', 'DET':'Detroit Red Wings', 'EDM':'Edmonton Oilers', 'FLA':'Florida Panthers',
'LAK':'Los Angeles Kings','MIN':'Minnesota Wild','MTL':'Montreal Canadiens','NSH':'Nashville Predators',
'NJD':'New Jersey Devils','NYI':'New York Islanders','NYR':'New York Rangers','OTT':'Ottawa Senators',
'PHI':'Philadelphia Flyers', 'PIT':'Pittsburgh Penguins','SJS':'San Jose Sharks',
'STL':'St. Louis Blues','TBL':'Tampa Bay Lightning', 'TOR':'Toronto Maple Leafs', 'VAN':'Vancouver Canucks',
'VGK':'Vegas Golden Knights', 'WSH':'Washington Capitals', 'WPJ':'Winnipeg Jets'}
reverse_team_mapping = {v: k for k, v in team_mapping.items()}
elo_scores.loc[:,'ShortTeam'] = elo_scores.loc[:,'Team']
elo_scores = elo_scores.replace({'ShortTeam':reverse_team_mapping})
elo_scores.index = elo_scores.ShortTeam



def prob_win(my_elo, your_elo):
    return 1/(1+10**(-(my_elo-your_elo)/400))

@lru_cache()
def pwin_wrapper(team_1,team_2):
    return prob_win(elo_scores.loc[team_1,'Elo'],elo_scores.loc[team_2,'Elo'])
bracket = ['NSH','COL','WPJ','MIN','VGK','LAK','ANA','SJS',
           'TBL','NJD','BOS','TOR','WSH','CBJ','PIT','PHI']

def random_draw(return_all = False):
    # keep track of games played
    gp = {k:0 for k in bracket}
    # set up lists
    round_2 = list()
    round_3 = list()
    finals = list()
    winner = list()
    # randomly play a bracket and determine next bracket
    def play_bracket(play_bracket,next_bracket):
        for i in range(len(play_bracket)):
            if i % 2:
                continue
            team_1 = play_bracket[i]
            team_2 = play_bracket[i+1]
            team_1_wins = 0
            team_2_wins = 0
            team_1_prob = pwin_wrapper(team_1,team_2)
            for i in range(7):
                if team_1_wins < 4 and team_2_wins < 4:
                    random_draw = random()
                    if random_draw < team_1_prob:
                        team_1_wins += 1
                    else:
                        team_2_wins += 1
                    if team_1_wins == 4:
                        next_bracket.append(team_1)
                    elif team_2_wins == 4:
                        next_bracket.append(team_2)
            gp[team_1] = gp[team_1] + team_1_wins
            gp[team_2] = gp[team_2] + team_2_wins
    # round 1
    play_bracket(bracket,round_2)
    # round 2
    play_bracket(round_2,round_3)
    # semi final
    play_bracket(round_3,finals)
    # final
    play_bracket(finals,winner)
    if return_all:
        return gp, bracket,round_2,round_3,finals,winner
    else:
        return gp



current_player_id = 0

common_head = '''<!doctype html><html lang-"en"><head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0,shrink-to-fit=no">
    {}
    <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js"></script>
    </head><body>
    '''
common_tail = '''<br><a href='/'>Home</a></body></html>'''
def roster_expected_goals(roster, nsim=1000):
    # add expected goals
    roster_goalsPG = dict()
    roster_player_team = dict()
    player_total = {k:0 for k in roster}
    for player in roster:
        roster_goalsPG[player] = player_df.loc[player,'PredictedPPG']
        roster_player_team[player] = player_df.loc[player,'team']
    # simulate brackets
    for i in range(nsim):
        gp = random_draw()
        for player in roster:
            player_total[player] = player_total[player] + gp[roster_player_team[player]] * roster_goalsPG[player]
    return sum([v for v in player_total.values()])/nsim

def get_player_margin(player_id, nsim=1000):
    value_without = roster_expected_goals(roster,nsim=nsim)
    alternate_roster = roster.copy()
    alternate_roster.add(player_id)
    value_with = roster_expected_goals(alternate_roster,nsim=nsim)
    return value_with - value_without

def get_info_on(player_id):
    if player_id == 0:
        return "not initialized"
    else:
        with Pool(processes=3) as pool:
            remaining_margin_points = sum(pool.starmap(get_player_margin, [(p,1000) for p in player_list]))
        remaining_cash = sum([k for k in bid_teams.values()])
        try:
            remaining_price = remaining_cash/remaining_margin_points
        except:
            remaining_price = 'No money left'
        player_margin = get_player_margin(player_id)
        player_price = player_margin * remaining_price
        txt = common_head.format('') + '''
        First Name: {} <br>
        Last Name: {} <br>
        Team: {} <br>
        Expected PPG: {:.2f} <br>
        Expected marginal points: {:.2f} <br>
        Expected games: {:.2f} <br>
        Value per point: {:.2f} <br>
        Player value at 100%: {:.2f} <br>
        Player value at 90%: {:.2f} <br>
        Player value at 80%: {:.2f} <br>
        Player value at 70%: {:.2f} <br>
        Player value at 60%: {:.2f} <br>
        Player value at 50%: {:.2f} <br>
        '''.format(player_df.loc[player_id,'FirstName'],
        player_df.loc[player_id,'LastName'],
        player_df.loc[player_id,'team'],
        player_df.loc[player_id,'PredictedPPG'],
        player_margin,
        player_margin/player_df.loc[player_id,'PredictedPPG'],
        remaining_price,
        player_price,
        player_price*.9,
        player_price*.8,
        player_price*.7,
        player_price*.6,
        player_price*.5)
        return txt

@app.route('/')
def root():
    return common_head.format('') + '''
    UUuugh. Web is hard.<br>
    Click for data entry mode: <a href="/set_player_form">here</a><br>
    Click for bidding mode: <a href="/current_player_info">here</a><br>
    Click for bidders overview: <a href="/teams">here</a><br>
    Click here for roster: <a href="/roster">here</a><br>
    </body></html>
    '''

@app.route('/teams')
def teams():
    return common_head.format('') + '<br>'.join(['Team {:02} ${}'.format(k,bid_teams[k]) for k in bid_teams.keys()]) + common_tail

@app.route('/roster')
def show_roster():
    return common_head.format('') + '<br>'.join(['{} {} {}'.format(player_df.loc[p,'FirstName'],
    player_df.loc[p,'LastName'],player_df.loc[p,'team']) for p in roster]) \
    + '<br>{} players left'.format(len(player_list)) + common_tail

@app.route('/current_player_info')
def current_player_info():
    return common_head.format('') + '''
    {}<br>
    Our cash: {}
    '''.format(get_info_on(current_player_id),bid_teams[our_id])+common_tail

# @app.route('/add_player/<player_id>')
# def add_player(player_id):
#     player_list.add(player_id)
#     return "Ok"

# @app.route('/list_players')
# def list_players():
#     return "\n".join(player_list)

@app.route('/set_player_form')
def player_form():
    return common_head.format('') + '''
    <form class="ui-filterable" action="/set_player">
    <input type="text" id="inset-autocomplete-input" data-type="search" placeholder="Don't fuck this up Nicholas">
    <input type="submit" value="Submit">
</form>
<ul data-role="listview" data-inset="true" data-filter="true" data-filter-reveal="true" data-input="#inset-autocomplete-input">
    <li><a href="#">Acura</a></li>
    <li><a href="#">Audi</a></li>
    <li><a href="#">BMW</a></li>
    <li><a href="#">Cadillac</a></li>
    <li><a href="#">Chrysler</a></li>
    <li><a href="#">Dodge</a></li>
    <li><a href="#">Ferrari</a></li>
    <li><a href="#">Ford</a></li>
    <li><a href="#">GMC</a></li>
    <li><a href="#">Honda</a></li>
    <li><a href="#">Hyundai</a></li>
    <li><a href="#">Infiniti</a></li>
    <li><a href="#">Jeep</a></li>
    <li><a href="#">Kia</a></li>
    <li><a href="#">Lexus</a></li>
    <li><a href="#">Mini</a></li>
    <li><a href="#">Nissan</a></li>
    <li><a href="#">Porsche</a></li>
    <li><a href="#">Subaru</a></li>
    <li><a href="#">Toyota</a></li>
    <li><a href="#">Volkswagen</a></li>
    <li><a href="#">Volvo</a></li>
</ul>
    '''+common_tail

@app.route('/sold_to_form')
def sold_to_form():
    return common_head.format('') + '''
     <form action="/sold_to">
      Player id:<br>
      Sold to:<br>
      <input type="text" name="buyer_team"><br>
      $ sold for:<br>
      <input type="text" name="sale_amount"><br>
      <input type="submit" value="Submit">
    </form>
    '''+common_tail

@app.route('/sold_to')
def sold_to():
    submitted_id = request.args.get('buyer_team')
    price = request.args.get('sale_amount')
    global player_list
    try:
        submitted_id = int(submitted_id)
        price = int(price)
    except:
        return common_head.format('<meta HTTP-EQUIV="REFRESH" content="2; url=/sold_to_form">') + '''
        You messed up <br>
        Team number {} <br>
        or price {} <br>
        are invalid. Redirecting you back.
        '''.format(submitted_id,price)+common_tail
    try:
        assert current_player_id in player_list
    except:
        return common_head.format(('<meta HTTP-EQUIV="REFRESH" content="2; url=/set_player_form">') ) + '''
        You messed up <br>
        Player {} was already sold.
        Redirecting you back to pick a new player.
        ''' + common_tail
    global bid_teams
    bid_teams[submitted_id] = bid_teams[submitted_id] - price
#     global player_list
    player_list.remove(current_player_id)
    first = player_df.loc[current_player_id,'FirstName']
    last = player_df.loc[current_player_id,'LastName']
    if submitted_id == our_id:
        global roster
        roster.add(current_player_id)
    return common_head.format('<meta HTTP-EQUIV="REFRESH" content="2; url=/set_player_form">') + '''
        Recorded sale of {} from {} to team {} for {}
        '''.format(first+' '+last, player_df.loc[current_player_id,'team'], submitted_id, price) + common_tail


@app.route('/set_player')
def current_player():
    submitted_id = request.args.get('id')
    try:
        submitted_id = int(submitted_id)
    except:
        submitted_id = '[not an integer: {}]'.format(submitted_id)
    if submitted_id not in player_df.index:
        return common_head.format('<meta name="viewport" content="width=device-width, initial-scale=1.0">') + '''
        You messed up. {} not a valid ID.<br>
        Redirecting you back to the submit page.<br>
        '''.format(submitted_id)+common_tail
    else:
        global current_player_id
        current_player_id = submitted_id
        first = player_df.loc[current_player_id,'FirstName']
        last = player_df.loc[current_player_id,'LastName']
        return common_head.format('<meta HTTP-EQUIV="REFRESH" content="2; url=/sold_to_form">') + '''
        Set player id to {}, {} from {}.<br>
        Click <a href="/sold_to_form">here</a> if not redirected.
        '''.format(current_player_id, first+' '+last, player_df.loc[current_player_id,'team'])+common_tail
