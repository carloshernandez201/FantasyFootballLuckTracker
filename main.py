
from pathlib import Path
from pathlib import Path
from yfpy.query import YahooFantasySportsQuery

daleague_id = '137827'
query = YahooFantasySportsQuery(
    league_id="137827",
    game_code="nfl",
    game_id=449,
    yahoo_consumer_key='dj0yJmk9cDA5ZUo0YWJGQkhUJmQ9WVdrOWVFOUJkMXB1TVVrbWNHbzlNQT09JnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PTc0',
    yahoo_consumer_secret='6af50cda9e062119b79f9c4c057385a2e736f6a6',
    env_file_location=Path(".env")
)

''' query.save_access_token_data_to_env_file(
    env_file_location=Path(".env"), 
    save_json_to_var_only=True
)'''

# Step 4: Fetch Data for the Selected League
print("Fetching league standings...") 



print("dada")
league_standings = query.get_league_scoreboard_by_week(1)
print("League Standings:")
print(league_standings)

print("SJE")
teams_list = []
teamsdata = query.get_league_teams()
print(teamsdata)

print('hello babt')
for elem in teamsdata:
    print(elem)
    teams_list.append(elem[1]['name'])

print(tuple(teams_list))


