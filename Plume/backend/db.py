import psycopg2

DB_config = {
    "dbname": "plumedata",
    "user": "app_user",
    "password": "user_password",
    "host": "localhost"
}

def init_db():
    conn = psycopg2.connect(**DB_config)
    cursor = conn.cursor()

    # ? users table
    cursor.exectue(
        '''
    CREATE TABLE IF NOT EXISTS "user"(
        id  SERIAL PRIMARY KEY,
        username    TEXT UNIQUE NOT NULL,
        password_hash   TEXT NOT NULL,
        questions_answered  INTERGER DEFAULT 0 NOT NULL
        );
        '''
    )
    # ? users answers
    cursor.execute(
        '''
    CREATE TABLE IF NOT EXISTS "answers"(
        id  SERIAL PRIMARY KEY,
        user_id INTERGER REFERENCES "user"(id) DELETE ON CASCADE,
        question TEXT NOT NULL,
        user_answer TEXT NOT NULL
        );
        '''
    )
    conn.commit()
    cursor.close()
    conn.close()

def get_db():
    conn = psycopg2.connect(**DB_config)
    return conn, conn.cursor()

