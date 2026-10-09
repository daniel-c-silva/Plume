from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
from db import get_db, init_db

app = Flask(__name__)
CORS(app)

init_db() 

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
def answer():
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

        cursor.execute( # increment the amount of times the user has answered a question
            '''
            UPDATE "user" 
            SET questions_answered = questions_answered + 1
            WHERE id = %s;
            ''',
            (user_id, )
        )

        cursor.execute( # save the data into our answers table for the specifc user id
            '''
            INSERT INTO "answers" (user_id, question, user_answer)
            VALUES (%s, %s, %s);
            ''',
            (user_id, question, user_answer)
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


if  __name__ == "__main__":
    print("Running server...")
    app.run(debug=True)