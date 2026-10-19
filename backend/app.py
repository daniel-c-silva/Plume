from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
from db import get_db, init_db
import ollama
from datetime import date

app = Flask(__name__)
CORS(app)
init_db()

# ! daily question updater (HELPERFUNCTION FOR DAILY QUESTION ROUTE)
def update_daily_question():
    today_str = str(date.today()) # define date to know if new question is needed
    conn = None
    # * check if the question has been generated today!
    try:
        conn, cursor = get_db()
        cursor.execute(
            'SELECT question FROM "daily_question" WHERE question_date = %s;', (today_str,)
        )
        stored_question = cursor.fetchone()
        if (stored_question): # * if it has
            return stored_question[0] #  Extracts the plain string text from the database tuple array
            
        try: # else, generate it using ollama
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
            question = response['message']['content'].strip()
        except Exception:
            question = "What is on your mind today?" # fall back question.
            
        try: #  save the question into the questions data base associated to the date
            cursor.execute(
                '''
                INSERT INTO "daily_question" (question_date, question)
                VALUES (%s, %s);
                ''',
                (today_str, question)
            )
            conn.commit()
        except Exception:
            if conn:
                conn.rollback()

        return question # * return the question so the app route can use it and send it back to the frontend
    finally:
        if conn:
            conn.close()

# ! registration route
@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    username = data.get('username') # look for username and password
    password = data.get('password')

    if ((not username) or (not password)):
        return jsonify({"error": "Missing information"}), 400
    
    conn = None
    try:
        hashed_password = generate_password_hash(password) # use genarate password hash to encrypt it
        conn, cursor = get_db()
        cursor.execute(
            'INSERT INTO "user" (username, password_hash) VALUES (%s, %s);', (username, hashed_password) # add the new user values into the data base
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
            'SELECT id, password_hash FROM "user" WHERE username = %s;', (username, )
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
    if (not data):
        return jsonify({"error": "Nothing was sent"}), 400
    user_id = data.get('user_id') # we get the user question and answer so we can look at it later
    question = data.get('question')
    user_answer = data.get('answer')
    if (not all([user_id, question, user_answer])):
        return jsonify({"error": "Missing required data"}), 400
    conn = None
    try:
        conn, cursor = get_db()
        
        # * Check if the user already answered this question manually to avoid ON CONFLICT database restrictions
        cursor.execute(
            'SELECT 1 FROM "answers" WHERE user_id = %s AND question = %s;',
            (user_id, question)
        )
        if cursor.fetchone(): # if the answer existed already in the db
            return jsonify({"error": "You already answered today's question."}), 400

        cursor.execute( # save the data into our answers table for the specifc user id
            '''
            INSERT INTO "answers" (user_id, question, user_answer)
            VALUES (%s, %s, %s);
            ''',
            (user_id, question, user_answer)
        )
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

# ! get data from asnweres
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
            'SELECT question, user_answer, id FROM "answers" WHERE user_id = %s;', (user_id, )
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
    question = update_daily_question()
    return jsonify({"question": question})

@app.route('/send-friend-request', methods=['POST'])
def add_friend():
    data = request.get_json() # get data from frontend
    if not data:
        return jsonify({"error": "No data"}), 400
    
    user_id = data.get('user_id') # sender 
    friend_username = data.get('friend_username') # friend username reciever of the request

    if not user_id or not friend_username:
        return jsonify({"error": "missing user id or friend username"}), 400

    conn = None

    try:
        conn, cursor = get_db()

        # * look up friend's id using their username
        cursor.execute('SELECT id FROM "user" WHERE username = %s', (friend_username, ))
        friend_row = cursor.fetchone() 

        if not friend_row:
            return jsonify({"error": "could not find friend id"}), 400

        friend_id = friend_row[0] # get the id from the list we fetched from the database.

        # prevent the user from adding themselves lmao
        if user_id == friend_id:
            return jsonify({"error": "why are you trying to add yourself as a friend?"})

        # * set as pending
        cursor.execute(
            '''
        INSERT INTO "friends" (user_id, friend_id, status)
        VALUES(%s, %s, 'pending...')
        ON CONFLICT DO NOTHING;
            ''',
        (user_id, friend_id)
        )
        conn.commit()

        return jsonify({"message": "friend request sent sucessfully"}), 200

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        if conn:
            conn.close()
        

@app.route('/accept-friend-request', methods=['POST'])
def accept_friend_request():
    data = request.get_json()
    user_id = data.get('user_id') # Reciever
    sender_username = data.get('sender_username') # sender

    if not user_id or not sender_username:
        return jsonify({"error": "Missing user_id or sender_id"}), 400

    conn = None
    try:
        conn, cursor = get_db()

        # Look up the sender's ID using their username
        cursor.execute('SELECT id FROM "user" WHERE username = %s;', (sender_username,))
        sender_row = cursor.fetchone()

        if not sender_row:
            return jsonify({"error": "User does not exist"}), 404

        sender_id = sender_row[0]

        # change the status to accepted
        cursor.execute(
            '''
            UPDATE "friends"
            SET status = 'accepted'
            WHERE user_id = %s AND friend_id = %s AND status = 'pending...';
            ''',
            (sender_id, user_id)
        )
        conn.commit()
        return jsonify({"message": f"friend request accepted! you're friends with {sender_username}"}), 200

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)})

    finally:
        if conn:
            conn.close()


@app.route('/pending-requests', methods=['POST'])
def get_pending_requests():
    data = request.get_json()
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    conn = None
    try:
        conn, cursor = get_db()
        cursor.execute(
            '''
        SELECT username 
        FROM "user" 
        WHERE id IN (
        SELECT user_id 
        FROM "friends" 
        WHERE friend_id = %s AND status = 'pending...');
            ''',
            (user_id,)
        )
        requests_data = cursor.fetchall()
        usernames = [r[0] for r in requests_data]
        return jsonify({"pending": usernames}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("empezando tiooooo arriba...")
    app.run(debug=True)
