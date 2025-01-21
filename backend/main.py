from flask import Flask, request, jsonify, g
import sqlite3
import jwt
import datetime
from functools import wraps
import bcrypt
from flask_cors import CORS  # Import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

DB_PATH = "vocabulary_app.db"
SECRET_KEY = "your_secret_key"
app.config['SECRET_KEY'] = SECRET_KEY

# Helper function to get a database connection
def get_db_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection

# Token validation decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            data = jwt.decode(token.split(' ')[1], app.config['SECRET_KEY'], algorithms=["HS256"])
            g.user_id = data['user_id']
        except:
            return jsonify({'message': 'Token is invalid'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/test', methods=['GET'])
def test():
    return "Server is running!"

# User registration
@app.route('/user/register', methods=['POST'])
def register():
    print("Registering user")
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO Users (username, password) VALUES (?, ?)",
            (username, hashed_password)
        )
        connection.commit()
    except sqlite3.IntegrityError:
        return jsonify({'message': 'Username already exists'}), 400
    finally:
        connection.close()

    # Return JWT for user
    connection = get_db_connection()
    cursor = connection.cursor()
    user = cursor.execute("SELECT * FROM Users WHERE username = ?", (username,)).fetchone()
    connection.close()

    token = jwt.encode(
        {'user_id': user['id'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
        app.config['SECRET_KEY'],
        algorithm="HS256"
    )

    return jsonify({'token': token}), 201

# User login
@app.route('/user/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    connection = get_db_connection()
    cursor = connection.cursor()
    user = cursor.execute("SELECT * FROM Users WHERE username = ?", (username,)).fetchone()
    connection.close()

    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        token = jwt.encode(
            {'user_id': user['id'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
            app.config['SECRET_KEY'],
            algorithm="HS256"
        )
        return jsonify({'token': token}), 200

    return jsonify({'message': 'Invalid username or password'}), 401

# Delete user account
@app.route('/user/delete', methods=['DELETE'])
@token_required
def delete_account():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM Users WHERE id = ?", (g.user_id,))
    connection.commit()
    connection.close()
    return jsonify({'message': 'Account deleted successfully'}), 200

# Get words for exercise
@app.route('/exercise', methods=['GET'])
@token_required
def get_exercise():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id, english, romanian FROM Words ORDER BY RANDOM() LIMIT 25")
    words = cursor.fetchall()

    connection.close()
    return jsonify([dict(row) for row in words])

# Record a session
@app.route('/session', methods=['POST'])
@token_required
def post_session():
    data = request.get_json()
    word_results = data.get('wordResults', [])  # List of tuples: [(word_id, correct), ...]
    timestamp = data.get('timestamp')
    duration = data.get('duration')

    if not word_results or timestamp is None or duration is None:
        return jsonify({"error": "Invalid payload"}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    # Calculate session stats
    correct_words = sum(1 for element in word_results if element['correct'])
    total_words = len(word_results)

    # Insert the session record
    cursor.execute(
        """
        INSERT INTO Sessions (user_id, timestamp, correct_words, total_words, duration)
        VALUES (?, ?, ?, ?, ?)
        """,
        (g.user_id, timestamp, correct_words, total_words, duration)
    )

    print(word_results)
    # Update the Words table for each word result
    for entry in word_results:
        print(f"Updating word {entry['wordId']} with correct={entry['correct']}")
        cursor.execute(
            """
            UPDATE Words
            SET practice_count = practice_count + 1,
                correct_count = correct_count + ?
            WHERE id = ?
            """,
            (1 if entry['correct'] else 0, entry['wordId'])
        )

    connection.commit()
    connection.close()

    return jsonify({"message": "Session recorded successfully"}), 201

@app.route('/history', methods=['GET'])
@token_required
def get_session_history():
    connection = get_db_connection()
    cursor = connection.cursor()

    # Get all sessions for the user
    cursor.execute(
        """
        SELECT timestamp, correct_words, total_words, duration
        FROM Sessions
        WHERE user_id = ?
        ORDER BY timestamp DESC
        """,
        (g.user_id,)
    )
    sessions = cursor.fetchall()

    # Initialize counters
    session_count = len(sessions)
    total_correct = sum(session['correct_words'] for session in sessions)
    total_words = sum(session['total_words'] for session in sessions)
    total_duration = sum(session['duration'] for session in sessions)

    # Get word statistics for most practiced, accurate, and difficult words

    # Most practiced words
    cursor.execute(
        """
        SELECT id, english, romanian, practice_count, correct_count
        FROM Words
        ORDER BY practice_count DESC
        LIMIT 10
        """
    )
    most_practiced_words = [
        {
            'id': word['id'],
            'english': word['english'],
            'romanian': word['romanian'],
            'correctCount': word['correct_count'],
            'totalCount': word['practice_count']
        }
        for word in cursor.fetchall()
    ]

    # Most accurate words (highest correct count to practice count ratio)
    cursor.execute(
        """
        SELECT id, english, romanian, correct_count, practice_count
        FROM Words
        WHERE practice_count > 0
        ORDER BY correct_count * 1.0 / practice_count DESC
        LIMIT 10
        """
    )
    most_accurate_words = [
        {
            'id': word['id'],
            'english': word['english'],
            'romanian': word['romanian'],
            'correctCount': word['correct_count'],
            'totalCount': word['practice_count']
        }
        for word in cursor.fetchall()
    ]

    # Most difficult words (lowest correct count to practice count ratio)
    cursor.execute(
        """
        SELECT id, english, romanian, correct_count, practice_count
        FROM Words
        WHERE practice_count > 0
        ORDER BY correct_count * 1.0 / practice_count ASC
        LIMIT 10
        """
    )
    most_difficult_words = [
        {
            'id': word['id'],
            'english': word['english'],
            'romanian': word['romanian'],
            'correctCount': word['correct_count'],
            'totalCount': word['practice_count']
        }
        for word in cursor.fetchall()
    ]

    connection.close()

    # Prepare the session history response
    session_history = {
        'history': [
            {
                'timestamp': session['timestamp'],
                'correct_words': session['correct_words'],
                'total_words': session['total_words'],
                'duration': session['duration']
            }
            for session in sessions
        ],
        'sessionCount': session_count,
        'totalCorrect': total_correct,
        'totalWords': total_words,
        'totalDuration': total_duration,
        'mostPracticedWords': most_practiced_words,
        'mostAccurateWords': most_accurate_words,
        'mostDifficultWords': most_difficult_words
    }

    return jsonify(session_history)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888, debug=True)

