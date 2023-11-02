import requests
import time
from datetime import datetime
from flask import Flask, jsonify, request
import threading

app = Flask(__name__)

report_configs = {}

user_data_storage = {}
blacklist = set()
date_format = "%Y-%m-%dT%H:%M"


def format_date_string(date_string):
    dash_count = 0
    formatted_date_string = ''
    for char in date_string:
        if char == '-':
            dash_count += 1
        if dash_count == 3:
            formatted_date_string += 'T'
            dash_count = 0
        else:
            formatted_date_string += char
    return formatted_date_string


def fetch_user_data(page_number):
    try:
        response = requests.get(f"https://sef.podkolzin.consulting/api/users/lastSeen?offset={page_number}")
        data = response.json()
        return data
    except Exception as e:
        print("Error when fetching user data:", repr(e))
        return None


def process_user_data(data):
    if not isinstance(data, dict) or 'data' not in data:
        print("Incorrect data format:", data)
        return

    user_list = data['data']
    for user_info in user_list:
        user_id = user_info.get('userId')
        is_online = user_info.get('isOnline')
        last_seen_str = user_info.get('lastSeenDate')
        username = user_info.get('nickname')  # Use 'nickname' as the field name
        current_time = datetime.now().strftime(date_format)

        if user_id in blacklist:
            continue
        if user_id not in user_data_storage:
            user_data_storage[user_id] = []

        last_intervals = user_data_storage[user_id]

        if is_online:
            if not last_intervals or (last_intervals and last_intervals[-1][1] is not None):
                user_data_storage[user_id].append([current_time, None, username])
        else:
            parts = last_seen_str.split(':')
            last_seen_str = ":".join(parts[:2])
            last_seen_datetime = datetime.strptime(last_seen_str, date_format)
            if last_intervals and last_intervals[-1][1] is None:
                last_intervals[-1][1] = last_seen_datetime
            else:
                user_data_storage[user_id].append([current_time, last_seen_datetime, username])


def update_user_data():
    page_number = 1
    while True:
        data = fetch_user_data(page_number)
        if data is None:
            pass
        else:
            process_user_data(data)

        if len(data.get('data', [])) > 0:
            page_number += 1
        else:
            break

        print("Waiting 30 seconds before the next attempt....")
        time.sleep(30)


@app.route('/user_intervals', methods=['GET'])
def get_user_intervals():
    return jsonify({user_id: intervals for user_id, intervals in user_data_storage.items() if user_id not in blacklist})


@app.route('/api/users/list', methods=['GET'])
def get_user_list():
    user_list = format_user_list()
    return jsonify(user_list)


def format_user_list():
    user_list = []
    for user_id, intervals in user_data_storage.items():
        if user_id not in blacklist:
            first_seen = intervals[0][0] if intervals else ""
            username = intervals[0][2] if intervals else ""
            user_info = {
                "username": username,
                "userId": user_id,
                "lastSeenDate": first_seen
            }
            user_list.append(user_info)
    return user_list


if __name__ == '__main__':
    data_update_thread = threading.Thread(target=update_user_data)
    data_update_thread.daemon = True
    data_update_thread.start()

    app.run(debug=True)

