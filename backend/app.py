from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
from db import get_db, init_db

app = Flask(__name__)
CORS(app)

init_db()

@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if ((not username) or (not password)):
        return  jsonify({"error": "Missing information"}), 400
    conn = None
    try:
        hashed_password = generate_password_hash(password)
        conn, cursor = get_db()

        cursor.execute(
        'INSERT INTO "user" (username, password_hash) VALUES (%s, %s);',
        (username, hashed_password)
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


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
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

        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if (not user):
            return jsonify({"error": "user does not exist."}), 401

        user_id = user[0]
        hashed_password = user[1]

        if (check_password_hash(hashed_password, password)):
            return jsonify({"message": "Login sucessfull", "User": user_id}), 200
        else:
            return jsonify({"error": "password did not match the user's"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if conn:
            conn.close()

        


if  __name__ == "__main__":
    print("Running server...")
    app.run(debug=True)