import psycopg2

DB_config = {
    "database": "plume_db",
    "user": "postgres",       # Must be "user", NOT "username"
    "password": "1234",
    "host": "localhost",      # Must be "host", NOT "server"
    "port": "5433"            # Remove "name" and "Driver" completely
}


def init_db():
    conn = psycopg2.connect(**DB_config)
    cursor = conn.cursor()

    # ? users table
    cursor.execute(
        '''
    CREATE TABLE IF NOT EXISTS "user"(
        id  SERIAL PRIMARY KEY,
        username    TEXT UNIQUE NOT NULL,
        password_hash   TEXT NOT NULL,
        questions_answered  INTEGER DEFAULT 0 NOT NULL
        );
        '''
    )
    # ? users answers
    cursor.execute(
        '''
    CREATE TABLE IF NOT EXISTS "answers"(
        id  SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE,
        question TEXT NOT NULL,
        user_answer TEXT NOT NULL
        );
        '''
    )
    # ? users friends
    cursor.execute(
        '''
    CREATE TABLE IF NOT EXISTS "friends"(
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE,
        friend_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE,
        status TEXT DEFAULT 'pending...' NOT NULL,
        CONSTRAINT unique_friendship UNIQUE (user_id, friend_id)
    );
        '''
    )
    conn.commit()
    cursor.close()
    conn.close()

def get_db():
    conn = psycopg2.connect(**DB_config)
    return conn, conn.cursor()

