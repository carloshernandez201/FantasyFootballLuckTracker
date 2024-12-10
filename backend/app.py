from flask import Flask, request, jsonify
from yfpy.query import YahooFantasySportsQuery
from flask_cors import CORS
import threading
import time
import subprocess
import pexpect
import os
import base64

import logging

logging.getLogger('werkzeug').setLevel(logging.ERROR)


def  clean_bytes_from_object( obj, visited=None):
    if visited is None:
        visited = set()
    obj_id = id(obj)
    if obj_id in visited:
        return obj
    visited.add(obj_id)
    """Recursively clean bytes from an object or its attributes."""
    if isinstance(obj, bytes):
        return obj.decode('utf-8')  # Decode bytes to string
    elif isinstance(obj, list):
        return [clean_bytes_from_object(item, visited) for item in obj]  # Clean each item in the list
    elif isinstance(obj, dict):
        return {key: clean_bytes_from_object(value, visited) for key, value in obj.items()}  # Clean dictionaries
    elif hasattr(obj, '__dict__'):  # Handle object attributes
        return {key: clean_bytes_from_object(value, visited) for key, value in vars(obj).items()}
    else:
        return obj  # Return other types as-is

class GlobalState:
    queryobj = None  # Static variable
    

    def setQuery(self, newQuery):
        self.queryobj = newQuery


app = Flask("Fraud Alert")
global_state = GlobalState()
#print("heyo")
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}}) # Allow only this origin

max_num_weeks = 12

daleague_id = None



@app.route('/')
def home():
    return "Hello, Flask!"

@app.route('/api/code', methods=['POST'])
def process_code():

    dacode = "dd"
    #print("hoj")
    data  = request.get_json()
    #print(data)
    dacode = data.get('verCode')
    os.environ['YFPY_VERIFIER'] = dacode
    return jsonify({"verCode": dacode})

'''def automate_yfpy_verifier(code):
    # Spawn the YFpy process
    process = pexpect.spawn('python -m yfpy')

    try:
        # Wait for the "Enter verifier:" prompt
        process.expect("Enter verifier:")
        print("Prompt detected. Sending verifier code...")

        # Send the verifier code
        process.sendline(code)

        # Wait for the process to complete
        process.expect(pexpect.EOF)
        output = process.before.decode('utf-8')  # Capture the process output
        print("YFpy Output:", output)

        return output
    except pexpect.ExceptionPexpect as e:
        print("Error automating YFpy:", e)
        return None'''


@app.route('/api/league', methods=['POST'])
def process_league():
    #print("hihi")
    data  = request.get_json()
    daleague_id = data.get('id')
    #print(daleague_id)
    if not daleague_id:
        return jsonify({"error": "Missing 'id' in request"}), 400

    
    thread = threading.Thread(target=send_query, args=(daleague_id,))
    thread.start()

    # Immediately return a response to the frontend
    return jsonify({"status": "query triggered", "id": daleague_id})

def send_query(leagueid):
    query = YahooFantasySportsQuery(
        league_id= leagueid,
        game_code="nfl",
        game_id=449,
        yahoo_consumer_key='dj0yJmk9cDA5ZUo0YWJGQkhUJmQ9WVdrOWVFOUJkMXB1TVVrbWNHbzlNQT09JnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PTc0',
        yahoo_consumer_secret='6af50cda9e062119b79f9c4c057385a2e736f6a6',
        #env_file_location=Path(".env")
    )
    global_state.setQuery(query)
    print(global_state.queryobj.get_league_teams()[0:43])
   # print("here ye" + str(daleague_id))
    return {"message": "Query sent successfully", "league_id": leagueid}




@app.route('/api/teams', methods=['POST'])
def process_teams():
    for _ in range(20):
        if global_state.queryobj:
            print("we got it")
            break
        time.sleep(1)
        print(_)
    print("quuery is")
    print(global_state.queryobj)

    teams = global_state.queryobj.get_league_teams()
    cleaned_teams = clean_bytes_from_object(teams)
    data = []
    print('hehe')
    for cleaned_team in cleaned_teams:
        
        # Recursively clean the team object
        # Access fields while handling team_logos correctly
        team_logo = cleaned_team['team_logos']['team_logo']  # Access 'team_logo' directly
        data.append({
            'list': cleaned_team['name'],
            'images': team_logo.url  # Access 'url' in 'team_logo'
        })
    print(data)
    print('o')
    
    return jsonify(data)



@app.route('/api/teams.<team>', methods=['POST', 'OPTIONS'])
def get_win_data(team):
    if request.method == 'OPTIONS':
        # Handle the preflight request
        response = jsonify({'message': 'CORS preflight successful'})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response, 200
    print('dahooooo')
    winsQuery = global_state.queryobj.get_league_standings()
    cleaned_wins_query = clean_bytes_from_object(winsQuery)
    print(cleaned_wins_query)
    print("shswy")
    win_ct = 0
    for teamData in cleaned_wins_query:
        if teamData['name'] == team:
            win_ct==1
    return jsonify({'expWins' : win_ct, 'wins' : win_ct})

'''@app.post('/api/SOSrank')
def findRank():
    teamInQuestion = request.get_json()['team']
    daleague_id = request.get_json()['league_id']
    )'''












if __name__ == '__main__':
    app.run(port=4000, debug=True)