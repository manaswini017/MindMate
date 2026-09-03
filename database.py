import sqlite3
import hashlib

DB_NAME = "mindmate.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    return sqlite3.connect(DB_NAME)


# ============================================================
# CREATE TABLES
# ============================================================

def create_tables():

    conn = get_connection()
    cursor = conn.cursor()

    # --------------------------------------------------------
    # USERS TABLE
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            language TEXT DEFAULT 'English',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # --------------------------------------------------------
    # GAME RESULTS TABLE
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS game_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            game_name TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            score INTEGER DEFAULT 0,
            accuracy REAL DEFAULT 0,
            attempts INTEGER DEFAULT 0,
            response_time REAL DEFAULT 0,
            played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # --------------------------------------------------------
    # REMINDERS TABLE
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            reminder_type TEXT NOT NULL,
            description TEXT NOT NULL,
            reminder_time TEXT NOT NULL,
            reminder_date TEXT,
            completed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


# ============================================================
# PASSWORD HASHING
# ============================================================

def hash_password(password):

    return hashlib.sha256(
        password.encode()
    ).hexdigest()


# ============================================================
# REGISTER USER
# ============================================================

def register_user(
    name,
    email,
    password,
    role,
    language="English"
):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        hashed_password = hash_password(password)

        cursor.execute("""
            INSERT INTO users
            (
                name,
                email,
                password,
                role,
                language
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            name,
            email,
            hashed_password,
            role,
            language
        ))

        conn.commit()

        return True, "Registration successful!"

    except sqlite3.IntegrityError:

        return False, "Email already registered."

    finally:

        conn.close()


# ============================================================
# LOGIN USER
# ============================================================

def login_user(email, password):

    conn = get_connection()
    cursor = conn.cursor()

    hashed_password = hash_password(password)

    cursor.execute("""
        SELECT
            id,
            name,
            email,
            role,
            language
        FROM users
        WHERE email = ?
        AND password = ?
    """, (
        email,
        hashed_password
    ))

    user = cursor.fetchone()

    conn.close()

    return user


# ============================================================
# SAVE GAME RESULT
# ============================================================

def save_game_result(
    user_id,
    game_name,
    difficulty,
    score,
    accuracy,
    attempts,
    response_time
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO game_results
        (
            user_id,
            game_name,
            difficulty,
            score,
            accuracy,
            attempts,
            response_time
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        game_name,
        difficulty,
        score,
        accuracy,
        attempts,
        response_time
    ))

    conn.commit()
    conn.close()


# ============================================================
# GET USER GAME RESULTS
# ============================================================

def get_user_game_results(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            game_name,
            difficulty,
            score,
            accuracy,
            attempts,
            response_time,
            played_at
        FROM game_results
        WHERE user_id = ?
        ORDER BY played_at DESC
    """, (user_id,))

    results = cursor.fetchall()

    conn.close()

    return results


# ============================================================
# GET USER STATISTICS
# ============================================================

def get_user_statistics(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            COUNT(*),
            AVG(accuracy),
            AVG(score)
        FROM game_results
        WHERE user_id = ?
    """, (user_id,))

    stats = cursor.fetchone()

    conn.close()

    return stats


# ============================================================
# GET RECENT GAME RESULTS
# ============================================================

def get_recent_game_results(
    user_id,
    limit=10
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            game_name,
            difficulty,
            score,
            accuracy,
            attempts,
            response_time,
            played_at
        FROM game_results
        WHERE user_id = ?
        ORDER BY played_at DESC
        LIMIT ?
    """, (
        user_id,
        limit
    ))

    results = cursor.fetchall()

    conn.close()

    return results


# ============================================================
# GET GAME AVERAGE
# ============================================================

def get_game_average(
    user_id,
    game_name
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            COUNT(*),
            AVG(score),
            AVG(accuracy)
        FROM game_results
        WHERE user_id = ?
        AND game_name = ?
    """, (
        user_id,
        game_name
    ))

    result = cursor.fetchone()

    conn.close()

    return result


# ============================================================
# GET LATEST GAME RESULT
# ============================================================

def get_latest_game_result(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            game_name,
            difficulty,
            score,
            accuracy,
            attempts,
            response_time,
            played_at
        FROM game_results
        WHERE user_id = ?
        ORDER BY played_at DESC
        LIMIT 1
    """, (user_id,))

    result = cursor.fetchone()

    conn.close()

    return result


# ============================================================
# ADD REMINDER
# ============================================================

def add_reminder(
    user_id,
    reminder_type,
    description,
    reminder_time,
    reminder_date
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO reminders
        (
            user_id,
            reminder_type,
            description,
            reminder_time,
            reminder_date
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        reminder_type,
        description,
        reminder_time,
        reminder_date
    ))

    conn.commit()
    conn.close()


# ============================================================
# GET USER REMINDERS
# ============================================================

def get_user_reminders(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            reminder_type,
            description,
            reminder_time,
            reminder_date,
            completed
        FROM reminders
        WHERE user_id = ?
        ORDER BY reminder_date, reminder_time
    """, (user_id,))

    reminders = cursor.fetchall()

    conn.close()

    return reminders


# ============================================================
# MARK REMINDER AS COMPLETED
# ============================================================

def complete_reminder(reminder_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE reminders
        SET completed = 1
        WHERE id = ?
    """, (reminder_id,))

    conn.commit()
    conn.close()


# ============================================================
# DELETE REMINDER
# ============================================================

def delete_reminder(reminder_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM reminders
        WHERE id = ?
    """, (reminder_id,))

    conn.commit()
    conn.close()


# ============================================================
# CAREGIVER - GET ALL ELDERLY USERS
# ============================================================

def get_elderly_users():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            email,
            language,
            created_at
        FROM users
        WHERE role = 'Elderly User'
        ORDER BY name
    """)

    users = cursor.fetchall()

    conn.close()

    return users


# ============================================================
# CAREGIVER - GET USER STATISTICS
# ============================================================

def get_caregiver_statistics(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            COUNT(*),
            AVG(score),
            AVG(accuracy),
            AVG(response_time)
        FROM game_results
        WHERE user_id = ?
    """, (user_id,))

    stats = cursor.fetchone()

    conn.close()

    return stats


# ============================================================
# CAREGIVER - GET USER GAME HISTORY
# ============================================================

def get_caregiver_game_history(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            game_name,
            difficulty,
            score,
            accuracy,
            attempts,
            response_time,
            played_at
        FROM game_results
        WHERE user_id = ?
        ORDER BY played_at DESC
    """, (user_id,))

    results = cursor.fetchall()

    conn.close()

    return results