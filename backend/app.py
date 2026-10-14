from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
from db import get_db, init_db
import ollama
from datetime import date
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
CORS(app)

cached_question = None
question_date = None

init_db() 



def update_daily_question():
    global current_question, question_date
    today = date.today()
    
    print(f"Generating new daily question for {today}...")
    try:
        response = ollama.chat(
            model='llama3.2',
            messages=[{
                'role': 'system',
                'content': 'You generate engaging daily icebreaker questions for close friends. Keep it under 15 words.'
            }, {
                'role': 'user',
                'content': 'Give me one fun daily question for today.'
            }]
        )
        current_question = response['message']['content'].strip()
    except Exception:
        current_question = "What is on your mind today?"
        
    question_date = today

scheduler = BackgroundScheduler() # init and start background scheduler
update_daily_question() # run imidiatly on start 
scheduler.add_job(func=update_daily_question, trigger="cron", hour = 0, minute = 0) # schedule for midnight
scheduler.start


# ! registration route
@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    username = data.get('username') # look for username and password
    password = data.get('password')

    if ((not username) or (not password)):
        return  jsonify({"error": "Missing information"}), 400
    conn = None
    try:
        hashed_password = generate_password_hash(password) # use genarate password hash to encrypt it
        conn, cursor = get_db()

        cursor.execute(
        'INSERT INTO "user" (username, password_hash) VALUES (%s, %s);', 
        (username, hashed_password) # add the new user values into the data base
        )

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "User profile created sucessfully"})
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        if conn:
            conn.close()


# ! login route
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username') # look for username and password in data
    password = data.get('password')

    if ((not username) or (not password)): 
        return jsonify({"error": "Missing information"}), 400
    conn = None
    try:
        conn, cursor = get_db()

        cursor.execute (
            'SELECT id, password_hash FROM "user" WHERE username = %s;',
            (username, )
        )

        user = cursor.fetchone() # user is now an array full of what we pulled

        cursor.close()
        conn.close()

        if (not user):
            return jsonify({"error": "user does not exist."}), 401

        user_id = user[0] # first index is the id
        hashed_password = user[1] # second is the pass hash

        if (check_password_hash(hashed_password, password)): # we use chck password hash to see if it matches the current recieved
            return jsonify({"message": "Login sucessfull", "User": user_id}), 200
        else:
            return jsonify({"error": "password did not match the user's"}), 401
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        if conn:
            conn.close()

# ! daily answer route
@app.route('/daily', methods=['POST'])
def daily():
    data = request.get_json() # get data

    if  (not data):
        return jsonify({"error": "Nothing was sent"}), 400

    user_id = data.get('user_id') # we get the user question and answer so we can look at it later
    question = data.get('question')
    user_answer = data.get('answer')

    if (not all([user_id, question, user_answer])):
        return jsonify({"error": "Missing required data"}), 400
    
    conn = None
    try:
        conn, cursor = get_db()


        cursor.execute( # save the data into our answers table for the specifc user id
            '''
            INSERT INTO "answers" (user_id, question, user_answer)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id, question) DO NOTHING;
            ''',
            (user_id, question, user_answer)
        )

        if (cursor.rowcount == 0): # nothing was inserted so they already asnwered
            return jsonify({"error": "You already answered today's question."}), 400


        cursor.execute( # increment the amount of times the user has answered a question
            '''
            UPDATE "user" 
            SET questions_answered = questions_answered + 1
            WHERE id = %s;
            ''',
            (user_id, )
        )

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"message": "Daily data was sucessfully recorded!"}), 200

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        if conn:
            conn.close()

# ! get data 
@app.route('/answers', methods=['POST'])
def get_data():
    data = request.get_json() # get data from frontend

    if (not data):
        return jsonify({"error": "could not find user id"})

    user_id = data.get('user_id') # get user

    conn = None

    try:
        conn, cursor = get_db()

        cursor.execute(
            'SELECT question, user_answer, id FROM "answers" WHERE user_id = %s;',
            (user_id, )
        )

        questiondata = cursor.fetchall() # make an array containing question and user

        cursor.close() 
        conn.close()

        answers = [{"question": i[0], "answer": i[1]} for i in questiondata]

        if (questiondata):
            return jsonify({"answers": answers}) # return the question and answer to the frontend
        
    except Exception as e:
        return jsonify({"error": str(e)})
    
    finally:
        if conn:
            conn.close()

# ! generate question
@app.route('/generate-daily-question', methods=['GET'])
def get_daily_question():
    return jsonify({"question": current_question})

    

if  __name__ == "__main__":
    print("Running server...")
    app.run(debug=True)