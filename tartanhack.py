# Imports
import urllib.request
import json

# Define API URLs and the API key
API_URL_STANDINGS = "https://api.football-data.org/v4/competitions/PL/standings"
API_KEY = "e3672a3115a64db2bcc8b4040090b619"

# The year that stats will be used
YEAR = 2024

# Define the headers for the API request
headers = {
    "X-Auth-Token": API_KEY
}

# Define the parameters for the API request
params = {
    "season": YEAR
}

# Encode the parameters into the URL
url = f"{API_URL_STANDINGS}?season={YEAR}"

# Create a request object with headers
req = urllib.request.Request(url, headers=headers)

# Send a request to get standings data
try:
    with urllib.request.urlopen(req) as response:
        data = response.read().decode('utf-8')
        standings = json.loads(data)
except urllib.error.URLError as e:
    print("Error fetching standings:", e)
    exit()


# Function to get detailed team information for a given team
def get_team_info(standings, team_name):
    standings_total = standings['standings'][0] # Season standings
    standings_home = standings['standings'][1] # Season standings for home games
    standings_away = standings['standings'][2] # Season standings for away games

    # Retrieves current form and season/home/away information
    team_season = next(team for team in standings_total["table"] if team['team']['shortName'] == team_name)
    team_home_season = next(team for team in standings_home["table"] if team['team']['shortName'] == team_name)
    team_away_season = next(team for team in standings_away["table"] if team['team']['shortName'] == team_name)

    return [
        team_season["form"], # current form
        team_season["won"], # season total wins
        team_season["lost"], # season total lost
        team_season["draw"], # season total draws
        team_home_season["won"], # season total home wins
        team_home_season["lost"], # season total home lost
        team_home_season["draw"], # season total home draws
        team_away_season["won"], # season total away wins
        team_away_season["lost"], # season total away lost
        team_away_season["draw"] # season total away draws
    ]

# Function to predict match outcome based on team form, stats, home game advantage
def predict_match(team1_form, team2_form, team1_status, team1_season, team2_season):

  # Assigns weight for each category
  form_win_weight = 5
  form_draw_weight = 2
  win_weight = 5
  draw_weight = 2
  lose_weight = 2
  home_advantage = 0.15

  # Initialize score for both teams
  team1_total = 0
  team2_total = 0

  # Calculate score for team's current form
  team1_form_score = (team1_form.count("W") * form_win_weight) + (team1_form.count("D") * form_draw_weight)
  team2_form_score = (team2_form.count("W") * form_win_weight) + (team2_form.count("D") * form_draw_weight)
  team1_total += team1_form_score
  team2_total += team2_form_score

  # Calculate score for team's season performance

  # Team 1
  if ((team1_season[0]*win_weight) - (team1_season[1]*lose_weight)) <= 0:
    team1_season_score = 0
  else:
    team1_season_score = ((team1_season[0]*win_weight) + (team1_season[2]*draw_weight)) - (team1_season[1]*lose_weight)

  team1_total += team1_season_score

  # Team 2
  if ((team2_season[0]*win_weight) - (team2_season[1]*lose_weight)) <= 0:
    team2_season_score = 0
  else:
    team2_season_score = ((team2_season[0]*win_weight) + (team2_season[2]*draw_weight)) - (team2_season[1]*lose_weight)

  team2_total += team2_season_score

  # Incorporate home game advantage into the scoring
  if team1_status == "yes":
    team1_total += (team1_total * home_advantage)
  else:
    team2_total += (team2_total * home_advantage)

  # Score total of both teams used for calculating win possibilities
  total_score = team1_total + team2_total

  # Calculates win possibilities for both teams
  if total_score > 0:
    team1_win_prob = team1_total / total_score
    team2_win_prob = team2_total / total_score
  else:
    # If no data, assume a draw
    team1_win_prob = 0.5
    team2_win_prob = 0.5

  # Turns into percentage
  team1_win_prob = team1_win_prob * 100
  team2_win_prob = team2_win_prob * 100

  # For cases of 100% chance of winning (not possible)
  if team1_win_prob == 100:
    team1_win_prob = 99

  if team2_win_prob == 100:
    team2_win_prob = 99

  # Print final outcomes
  print("\n\n\nCalculating results...\n\n")
  print(f"\nTeam 1 total score: {team1_total}")
  print(f"Team 2 total score: {team2_total}")
  print(f"\n{team1}'s win probability: {team1_win_prob:.2f}%")
  print(f"{team2}'s win probability: {team2_win_prob:.2f}%")

# Get user input for team names
def get_team_input(team_names, prompt):
    while True:
        team = input(prompt).strip().lower()  # Convert user input to lowercase

        # Compare lowercase versions of the team names
        if team not in [t.lower() for t in team_names]:  # Compare lowercase versions of the team names
            print(f"\nInvalid team name. Please pick a valid team from the list.\n")
        else:
            # Return the properly capitalized team name from the original list
            return next(t for t in team_names if t.lower() == team)

# Get user input for yes/no
def get_home_input(prompt):
    while True:
        response = input(prompt).strip().lower()
        if response == "yes" or response == "no":
            return response
        else:
            print("\nInvalid input. Please answer with 'yes' or 'no'.\n")

# Main code to fetch and display team data
if standings:

    print("Below contains the list of the 20 Premier League Teams")
    print("You will be asked to choose 2 of the 20 teams for a match prediction\n")

    standings_total = standings['standings'][0]["table"]  # Get the standings table
    team_names = []
    for team_data in standings_total:
        team_names.append(team_data['team']['shortName'])  # Retrieves team names from the standings

    # Split the teamNames list into two parts
    team_first_half = team_names[:10]
    team_second_half = team_names[10:20]

    # Print the two arrays of team names
    print(", ".join(team_first_half) + ",")
    print(", ".join(team_second_half))

    print("\n\nPlease pick a team from the above with exact spelling: ")

    # Get user input
    team1 = get_team_input(team_names, "Pick Team 1: ")
    team1_status = get_home_input(f"Is {team1} playing at home? [yes/no]: ")
    team2 = get_team_input(team_names, "Pick Team 2: ")
    print("\n\n" + "-"*80)

    # Retrieve the detailed team information for both teams
    team1_info = get_team_info(standings, team1)
    team2_info = get_team_info(standings, team2)
    team1_form = team1_info[0]
    team2_form = team2_info[0]

    # Organize team season stats (wins, losses, draws)
    team1_season = (team1_info[1], team1_info[2], team1_info[3])  # (Wins, Losses, Draws)
    team1_home_season = (team1_info[4], team1_info[5], team1_info[6]) # Home stats
    team1_away_season = (team1_info[7], team1_info[8], team1_info[9]) # Away stats

    team2_season = (team2_info[1], team2_info[2], team2_info[3])  # (Wins, Losses, Draws)
    team2_home_season = (team2_info[4], team2_info[5], team2_info[6]) # Home stats
    team2_away_season = (team2_info[7], team2_info[8], team2_info[9]) # Away stats

    # Print stats for both teams
    print(f"\n\n{team1}'s current form: " + team1_form)
    print(f"\nSeason stats for {team1}:\nWins: {team1_season[0]}, Losses: {team1_season[1]}, Draws: {team1_season[2]}")
    print(f"\nHome game stats for {team1}:\nWins: {team1_home_season[0]}, Losses: {team1_home_season[1]}, Draws: {team1_home_season[2]}")
    print(f"\nAway game stats for {team1}:\nWins: {team1_away_season[0]}, Losses: {team1_away_season[1]}, Draws: {team1_away_season[2]}")

    print(f"\n\n{team2}'s current form: " + team2_form)
    print(f"\nSeason stats for {team2}:\nWins: {team2_season[0]}, Losses: {team2_season[1]}, Draws: {team2_season[2]}")
    print(f"\nHome game stats for {team2}:\nWins: {team2_home_season[0]}, Losses: {team2_home_season[1]}, Draws: {team2_home_season[2]}")
    print(f"\nAway game stats for {team2}:\nWins: {team2_away_season[0]}, Losses: {team2_away_season[1]}, Draws: {team2_away_season[2]}")

else:
    print("Error: Failed to retrieve standings.")

# Calls the predictMatch function
predict_match(team1_form, team2_form, team1_status, team1_season, team2_season)