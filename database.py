
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("peerbridge.db")

# Only these tables and columns can be managed through the explorer.
TABLES = {
    "students": [
        "id", "name", "email", "department", "year"
    ],
    "skills": [
        "id", "student_id", "name", "skill_type", "level"
    ],
    "requests": [
        "id", "student_id", "requested_skill", "offer_skill",
        "details", "status", "created_at"
    ],
    "sessions": [
        "id", "learner_id", "tutor_id", "topic",
        "session_time", "status"
    ],
    "reviews": [
        "id", "session_id", "rating", "comment", "created_at"
    ],
}


def connect():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 10000")
    return conn


def init_db():
    with connect() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            department TEXT NOT NULL,
            year TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            skill_type TEXT NOT NULL
                CHECK(skill_type IN ('Can teach','Wants to learn')),
            level TEXT NOT NULL,
            FOREIGN KEY(student_id) REFERENCES students(id)
                ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            requested_skill TEXT NOT NULL,
            offer_skill TEXT,
            details TEXT,
            status TEXT NOT NULL DEFAULT 'Open',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(student_id) REFERENCES students(id)
                ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            learner_id INTEGER NOT NULL,
            tutor_id INTEGER NOT NULL,
            topic TEXT NOT NULL,
            session_time TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Scheduled',
            FOREIGN KEY(learner_id) REFERENCES students(id)
                ON DELETE CASCADE,
            FOREIGN KEY(tutor_id) REFERENCES students(id)
                ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
            comment TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(session_id) REFERENCES sessions(id)
                ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_skills_student
            ON skills(student_id);

        CREATE INDEX IF NOT EXISTS idx_skills_name
            ON skills(name);

        CREATE INDEX IF NOT EXISTS idx_skills_type
            ON skills(skill_type);

        CREATE INDEX IF NOT EXISTS idx_requests_student
            ON requests(student_id);

        CREATE INDEX IF NOT EXISTS idx_requests_status
            ON requests(status);

        CREATE INDEX IF NOT EXISTS idx_requests_created
            ON requests(created_at);

        CREATE INDEX IF NOT EXISTS idx_sessions_learner
            ON sessions(learner_id);

        CREATE INDEX IF NOT EXISTS idx_sessions_tutor
            ON sessions(tutor_id);

        CREATE INDEX IF NOT EXISTS idx_sessions_time
            ON sessions(session_time);

        CREATE INDEX IF NOT EXISTS idx_reviews_session
            ON reviews(session_id);

        CREATE TRIGGER IF NOT EXISTS prevent_duplicate_student_email
        BEFORE INSERT ON students
        WHEN NEW.email IS NOT NULL AND TRIM(NEW.email) != ''
        AND EXISTS (
            SELECT 1 FROM students
            WHERE lower(email) = lower(NEW.email)
        )
        BEGIN
            SELECT RAISE(ABORT, 'That email is already registered.');
        END;

        CREATE TRIGGER IF NOT EXISTS prevent_duplicate_student_email_update
        BEFORE UPDATE OF email ON students
        WHEN NEW.email IS NOT NULL AND TRIM(NEW.email) != ''
        AND EXISTS (
            SELECT 1 FROM students
            WHERE lower(email) = lower(NEW.email)
            AND id != OLD.id
        )
        BEGIN
            SELECT RAISE(ABORT, 'That email is already registered.');
        END;

        CREATE TRIGGER IF NOT EXISTS prevent_same_session_students
        BEFORE INSERT ON sessions
        WHEN NEW.learner_id = NEW.tutor_id
        BEGIN
            SELECT RAISE(ABORT, 'Learner and tutor must be different students.');
        END;
        """)


# ---------------- STUDENTS ----------------

def add_student(name, email, department, year):
    try:
        with connect() as conn:
            if email and email.strip():
                exists = conn.execute(
                    "SELECT id FROM students WHERE lower(email)=lower(?)",
                    (email.strip(),)
                ).fetchone()
                if exists:
                    return False, "That email is already registered."

            conn.execute(
                """INSERT INTO students(name,email,department,year)
                   VALUES(?,?,?,?)""",
                (name, email, department, year)
            )
        return True, "Student added successfully."
    except sqlite3.Error as e:
        return False, str(e)


def get_students():
    with connect() as conn:
        return conn.execute(
            """SELECT id,name,email,department,year
               FROM students ORDER BY name"""
        ).fetchall()


# ---------------- SKILLS ----------------

def add_skill(student_id, name, skill_type, level):
    with connect() as conn:
        conn.execute(
            """INSERT INTO skills(student_id,name,skill_type,level)
               VALUES(?,?,?,?)""",
            (student_id, name, skill_type, level)
        )


def get_skills():
    with connect() as conn:
        return conn.execute("""
            SELECT skills.id, students.name, skills.name,
                   skills.skill_type, skills.level
            FROM skills
            JOIN students ON students.id=skills.student_id
            ORDER BY students.name
        """).fetchall()


# ---------------- REQUESTS ----------------

def create_request(student_id, requested_skill, offer_skill, details):
    with connect() as conn:
        conn.execute("""
            INSERT INTO requests(
                student_id,requested_skill,offer_skill,details
            ) VALUES(?,?,?,?)
        """, (student_id, requested_skill, offer_skill, details))


def get_requests():
    with connect() as conn:
        return conn.execute("""
            SELECT requests.id, students.name,
                   requests.requested_skill,
                   COALESCE(requests.offer_skill, '') ||
                   CASE
                       WHEN requests.details IS NOT NULL
                       AND requests.details != ''
                       THEN ' — ' || requests.details
                       ELSE ''
                   END,
                   requests.status, requests.created_at
            FROM requests
            JOIN students ON students.id=requests.student_id
            ORDER BY requests.id DESC
        """).fetchall()


# ---------------- SESSIONS ----------------

def create_session(learner_id, tutor_id, topic, session_time):
    if learner_id == tutor_id:
        raise ValueError("Learner and tutor must be different students.")

    with connect() as conn:
        conn.execute("""
            INSERT INTO sessions(
                learner_id,tutor_id,topic,session_time
            ) VALUES(?,?,?,?)
        """, (learner_id, tutor_id, topic, session_time))


def get_sessions():
    with connect() as conn:
        return conn.execute("""
            SELECT sessions.id, learner.name, tutor.name,
                   sessions.topic, sessions.session_time, sessions.status
            FROM sessions
            JOIN students learner ON learner.id=sessions.learner_id
            JOIN students tutor ON tutor.id=sessions.tutor_id
            ORDER BY sessions.session_time DESC
        """).fetchall()


# ---------------- REVIEWS ----------------

def add_review(session_id, rating, comment):
    if not 1 <= int(rating) <= 5:
        raise ValueError("Rating must be between 1 and 5.")

    with connect() as conn:
        conn.execute("""
            INSERT INTO reviews(session_id,rating,comment)
            VALUES(?,?,?)
        """, (session_id, rating, comment))


def get_reviews():
    with connect() as conn:
        return conn.execute("""
            SELECT reviews.id, sessions.topic,
                   reviews.rating, reviews.comment
            FROM reviews
            JOIN sessions ON sessions.id=reviews.session_id
            ORDER BY reviews.id DESC
        """).fetchall()


# ---------------- MATCHING ----------------

def find_matches(topic, offer):
    topic = topic.strip().lower()
    offer = offer.strip().lower()

    if not topic:
        return []

    with connect() as conn:
        rows = conn.execute("""
            SELECT DISTINCT students.id, students.name,
                students.department,
                GROUP_CONCAT(
                    CASE WHEN skills.skill_type='Can teach'
                    THEN skills.name END
                ),
                GROUP_CONCAT(
                    CASE WHEN skills.skill_type='Wants to learn'
                    THEN skills.name END
                )
            FROM students
            JOIN skills ON skills.student_id=students.id
            GROUP BY students.id
        """).fetchall()

    matches = []

    for row in rows:
        can_teach = (row[3] or "").lower()
        wants = (row[4] or "").lower()

        if topic in can_teach and (
            not offer or offer in wants or offer in can_teach
        ):
            matches.append(row)

    if not matches:
        for row in rows:
            if topic in (row[3] or "").lower():
                matches.append(row)

    return matches


# ==================================================
# DATABASE MANAGEMENT / EXPLORER FUNCTIONS
# ==================================================

def get_table_names():
    return list(TABLES.keys())


def get_table_counts():
    counts = {}

    with connect() as conn:
        for table in TABLES:
            counts[table] = conn.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]

    return counts


def get_table_data(table, search=""):
    if table not in TABLES:
        raise ValueError("Invalid table name.")

    columns = TABLES[table]
    sql = f"SELECT {', '.join(columns)} FROM {table}"
    params = []

    if search.strip():
        conditions = [
            f"CAST({column} AS TEXT) LIKE ?"
            for column in columns
        ]
        sql += " WHERE " + " OR ".join(conditions)
        params = [f"%{search.strip()}%"] * len(columns)

    sql += f" ORDER BY {columns[0]} DESC"

    with connect() as conn:
        return conn.execute(sql, params).fetchall()


def get_table_columns(table):
    if table not in TABLES:
        raise ValueError("Invalid table name.")

    with connect() as conn:
        table_info = conn.execute(
            f"PRAGMA table_info({table})"
        ).fetchall()

    # Return column names only, not SQLite metadata tuples.
    return [column[1] for column in table_info]


def update_record(table, record_id, values):
    if table not in TABLES:
        raise ValueError("Invalid table name.")

    allowed = [
        column for column in TABLES[table]
        if column != "id"
    ]

    if not values:
        raise ValueError("No changes were supplied.")

    for column in values:
        if column not in allowed:
            raise ValueError(f"Invalid column: {column}")

    assignments = ", ".join(
        f"{column}=?" for column in values
    )

    sql = (
        f"UPDATE {table} SET {assignments} WHERE id=?"
    )

    parameters = list(values.values()) + [record_id]

    with connect() as conn:
        cursor = conn.execute(sql, parameters)

        if cursor.rowcount == 0:
            return False, "Record not found."

    return True, "Record updated successfully."


def delete_record(table, record_id):
    if table not in TABLES:
        raise ValueError("Invalid table name.")

    with connect() as conn:
        cursor = conn.execute(
            f"DELETE FROM {table} WHERE id=?",
            (record_id,)
        )

        if cursor.rowcount == 0:
            return False, "Record not found."

    return True, "Record deleted successfully."


def database_health():
    with connect() as conn:
        integrity = conn.execute(
            "PRAGMA integrity_check"
        ).fetchone()[0]

        foreign_key_errors = conn.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        database_size = (
            DB_PATH.stat().st_size if DB_PATH.exists() else 0
        )

        return {
            "integrity": integrity,
            "foreign_key_errors": foreign_key_errors,
            "database_size_bytes": database_size,
            "database_path": str(DB_PATH),
            "table_counts": get_table_counts()
        }


def get_database_schema():
    schema = {}

    with connect() as conn:
        for table in TABLES:
            schema[table] = {
                "columns": conn.execute(
                    f"PRAGMA table_info({table})"
                ).fetchall(),
                "foreign_keys": conn.execute(
                    f"PRAGMA foreign_key_list({table})"
                ).fetchall(),
                "indexes": conn.execute(
                    f"PRAGMA index_list({table})"
                ).fetchall()
            }

    return schema
