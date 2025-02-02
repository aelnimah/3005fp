import json
import psycopg2
import os

host = "localhost"
database = input("DB Name: ")
user = input("DB User: ")
password = input("DB Password: ")
port = "5432"

conn = psycopg2.connect(host=host, database=database, user=user, password=password, port=port)
cursor = conn.cursor()

base_dir = '../json_loader'
season_files = ['90.json', '44.json', '42.json', '4.json']
events_path = os.path.join(base_dir, 'events')

insert_sql = """
INSERT INTO Goals (event_id, goal_type, assist_event_id, shot_id)
VALUES (%s, %s, %s, %s) ON CONFLICT (event_id) DO NOTHING;
"""

for season_file in season_files:
    filepath = os.path.join(base_dir, season_file)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as file:
            matches = json.load(file)
            for match in matches:
                match_id = match['match_id']
                event_file_path = os.path.join(events_path, f'{match_id}.json')
                if os.path.exists(event_file_path):
                    with open(event_file_path, 'r', encoding='utf-8') as event_file:
                        events = json.load(event_file)
                        for event in events:
                            if event['type']['name'] == "Shot" and event['shot'].get('outcome', {}).get('name') == "Goal":
                                event_id = event['id']
                                goal_type = event['shot']['type']['name']
                                assist_event_id = event['shot'].get('key_pass_id', None)
                                shot_id = event_id

                                cursor.execute(insert_sql, (event_id, goal_type, assist_event_id, shot_id))

conn.commit()
cursor.close()
conn.close()

print("Goals data successfully processed and inserted.")
