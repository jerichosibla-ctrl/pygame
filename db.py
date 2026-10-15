import os
import hashlib
import importlib


try:
    mysql_connector = importlib.import_module("mysql.connector")
    MySQLError = mysql_connector.Error
except (ImportError, AttributeError):
    mysql_connector = None

    class MySQLError(Exception):
        """Fallback exception used when mysql-connector-python is unavailable."""

        pass


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "space_invaders_sibla")


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection(include_database=True):
    connection = None

    try:
        if mysql_connector is None:
            raise MySQLError(
                "mysql-connector-python is not installed. "
                "Install it with: pip install mysql-connector-python"
            )

        connection_options = {
            "host": DB_HOST,
            "port": DB_PORT,
            "user": DB_USER,
            "password": DB_PASSWORD,
        }

        if include_database:
            connection_options["database"] = DB_NAME

        connection = mysql_connector.connect(**connection_options)

        return connection

    except MySQLError as e:
        print(f"Database connection error: {e}")
        return None


# ============================================================
# PASSWORD HASHING
# ============================================================

def hash_password(password):
    """
    Convert a password into a SHA-256 hash.
    """

    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


# ============================================================
# INITIALIZE DATABASE TABLES
# ============================================================

def initialize_database():
    connection = None
    cursor = None

    try:
        # Connect without a default schema first so a fresh installation can
        # create the application database before creating its tables.
        connection = get_connection(include_database=False)

        if connection is None:
            print("Database connection failed.")
            return False

        cursor = connection.cursor()

        database_name = DB_NAME.replace("`", "``")
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{database_name}`"
        )
        cursor.close()
        cursor = None
        connection.close()
        connection = get_connection()

        if connection is None:
            print("Database connection failed after database creation.")
            return False

        cursor = connection.cursor()

        # ----------------------------------------------------
        # PLAYERS TABLE
        # ----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                player_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                full_name VARCHAR(100) NOT NULL,
                email VARCHAR(100),
                level INT NOT NULL DEFAULT 1,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    ON UPDATE CURRENT_TIMESTAMP
            )
        """)

        # ----------------------------------------------------
        # SCORES TABLE
        # ----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scores (
                score_id INT AUTO_INCREMENT PRIMARY KEY,
                player_id INT NOT NULL,
                score INT NOT NULL DEFAULT 0,
                level INT NOT NULL DEFAULT 1,
                played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                CONSTRAINT fk_scores_player
                FOREIGN KEY (player_id)
                REFERENCES players(player_id)
                ON DELETE CASCADE
                ON UPDATE CASCADE
            )
        """)

        connection.commit()

        print("Database tables initialized successfully.")
        return True

    except MySQLError as e:
        print(f"Error creating tables: {e}")
        return False

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


# ============================================================
# REGISTER PLAYER
# ============================================================

def register_player(player_name, password):
    connection = None
    cursor = None

    try:
        connection = get_connection()

        if connection is None:
            print("Database connection failed.")
            return False, "Database connection failed. Start MySQL and try again."

        cursor = connection.cursor()

        # Check if username already exists
        cursor.execute(
            """
            SELECT player_id
            FROM players
            WHERE username = %s
            """,
            (player_name,)
        )

        existing_player = cursor.fetchone()

        if existing_player:
            print("Username already exists.")
            return False, "Username already exists."

        password_hash = hash_password(password)

        cursor.execute(
            """
            INSERT INTO players (
                username,
                full_name,
                password_hash
            )
            VALUES (%s, %s, %s)
            """,
            (
                player_name,
                player_name,
                password_hash
            )
        )

        connection.commit()

        print("Registration successful.")
        return True, "Registration successful."

    except MySQLError as e:
        print(f"Registration error: {e}")
        return False, "Registration failed."

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


# ============================================================
# LOGIN PLAYER
# ============================================================

def login_player(player_name, password):
    connection = None
    cursor = None

    try:
        connection = get_connection()

        if connection is None:
            print("Database connection failed.")
            return None, "Database connection failed. Start MySQL and try again."

        cursor = connection.cursor()

        password_hash = hash_password(password)

        cursor.execute(
            """
            SELECT
                player_id,
                username
            FROM players
            WHERE username = %s
            AND password_hash = %s
            """,
            (
                player_name,
                password_hash
            )
        )

        player = cursor.fetchone()

        if player:
            print("Login successful.")

            return {
                "id": player[0],
                "player_name": player[1]
            }, "Login successful."

        print("Invalid username or password.")
        return None, "Invalid username or password."

    except MySQLError as e:
        print(f"Login error: {e}")
        return None, "Login failed."

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


# ============================================================
# SAVE SCORE
# ============================================================

def save_score(player_id, score):
    connection = None
    cursor = None

    try:
        connection = get_connection()

        if connection is None:
            print("Database connection failed.")
            return False

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO scores (
                player_id,
                score
            )
            VALUES (%s, %s)
            """,
            (
                player_id,
                score
            )
        )

        connection.commit()

        return True

    except MySQLError as e:
        print(f"Error saving score: {e}")
        return False

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


# ============================================================
# GET HIGH SCORES
# ============================================================

def get_high_scores(limit=10):
    connection = None
    cursor = None

    try:
        connection = get_connection()

        if connection is None:
            print("Database connection failed.")
            return []

        cursor = connection.cursor()

        limit = int(limit)

        if limit < 1:
            limit = 10

        if limit > 100:
            limit = 100

        query = f"""
            SELECT
                players.username,
                scores.score,
                scores.played_at
            FROM scores
            INNER JOIN players
                ON scores.player_id = players.player_id
            ORDER BY
                scores.score DESC,
                scores.played_at ASC
            LIMIT {limit}
        """

        cursor.execute(query)

        results = cursor.fetchall()

        return results

    except (MySQLError, ValueError) as e:
        print(f"Error getting high scores: {e}")
        return []

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


# ============================================================
# GET PLAYER SCORES
# ============================================================

def get_player_scores(player):
    connection = None
    cursor = None

    try:
        connection = get_connection()

        if connection is None:
            print("Database connection failed.")
            return []

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                scores.score,
                scores.played_at
            FROM scores
            INNER JOIN players
                ON scores.player_id = players.player_id
            WHERE players.player_id = %s
               OR players.username = %s
            ORDER BY scores.score DESC
            """,
            (player, player)
        )

        results = cursor.fetchall()

        return results

    except MySQLError as e:
        print(f"Error getting player scores: {e}")
        return []

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


# ============================================================
# UPDATE PLAYER PROFILE
# ============================================================

def update_player_profile(
    player_id,
    new_username=None,
    new_password=None
):
    connection = None
    cursor = None

    try:
        connection = get_connection()

        if connection is None:
            print("Database connection failed.")
            return False

        cursor = connection.cursor()

        # ----------------------------------------------------
        # UPDATE USERNAME ONLY
        # ----------------------------------------------------

        if new_username and not new_password:

            cursor.execute(
                """
                SELECT player_id
                FROM players
                WHERE username = %s
                AND player_id != %s
                """,
                (
                    new_username,
                    player_id
                )
            )

            existing_player = cursor.fetchone()

            if existing_player:
                print("Username is already taken.")
                return False

            cursor.execute(
                """
                UPDATE players
                SET username = %s,
                    full_name = %s
                WHERE player_id = %s
                """,
                (
                    new_username,
                    new_username,
                    player_id
                )
            )

        # ----------------------------------------------------
        # UPDATE PASSWORD ONLY
        # ----------------------------------------------------

        elif new_password and not new_username:

            password_hash = hash_password(new_password)

            cursor.execute(
                """
                UPDATE players
                SET password_hash = %s
                WHERE player_id = %s
                """,
                (
                    password_hash,
                    player_id
                )
            )

        # ----------------------------------------------------
        # UPDATE USERNAME AND PASSWORD
        # ----------------------------------------------------

        elif new_username and new_password:

            cursor.execute(
                """
                SELECT player_id
                FROM players
                WHERE username = %s
                AND player_id != %s
                """,
                (
                    new_username,
                    player_id
                )
            )

            existing_player = cursor.fetchone()

            if existing_player:
                print("Username is already taken.")
                return False

            password_hash = hash_password(new_password)

            cursor.execute(
                """
                UPDATE players
                SET
                    username = %s,
                    full_name = %s,
                    password_hash = %s
                WHERE player_id = %s
                """,
                (
                    new_username,
                    new_username,
                    password_hash,
                    player_id
                )
            )

        else:
            print("No profile changes provided.")
            return False

        if cursor.rowcount == 0:
            print("Player account was not found.")
            return False

        connection.commit()

        print("Profile updated successfully.")
        return True

    except MySQLError as e:
        print(f"Error updating profile: {e}")

        if connection is not None:
            connection.rollback()

        return False

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


# ============================================================
# TEST CONNECTION
# ============================================================

def test_connection():
    connection = None

    try:
        connection = get_connection()

        if connection is not None and connection.is_connected():
            print("Database connection successful.")
            return True

        print("Database connection failed.")
        return False

    except MySQLError as e:
        print(f"Database connection error: {e}")
        return False

    finally:
        if connection is not None and connection.is_connected():
            connection.close()


# ============================================================
# RUN DATABASE INITIALIZATION
# ============================================================

if __name__ == "__main__":
    if test_connection():
        if initialize_database():
            print("Space Invaders database is ready.")
        else:
            print("Could not initialize database.")