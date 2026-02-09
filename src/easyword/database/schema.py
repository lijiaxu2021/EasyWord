# SQL Schema definitions

CREATE_LIBRARIES_TABLE = """
CREATE TABLE IF NOT EXISTS libraries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# Insert default library if not exists
INSERT_DEFAULT_LIBRARY = """
INSERT OR IGNORE INTO libraries (id, name, description) VALUES (1, '默认词库', '系统默认词库');
"""

CREATE_WORDS_TABLE = """
CREATE TABLE IF NOT EXISTS words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uid TEXT UNIQUE, -- Globally Unique ID for sync
    library_id INTEGER DEFAULT 1,
    word TEXT NOT NULL,
    phonetic TEXT,
    definition_cn TEXT, 
    definition_en TEXT,
    example TEXT, 
    level INTEGER DEFAULT 1,
    category TEXT,
    tags TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (library_id) REFERENCES libraries (id),
    UNIQUE(library_id, word)
);
"""

CREATE_USER_PROGRESS_TABLE = """
CREATE TABLE IF NOT EXISTS user_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_id INTEGER NOT NULL,
    status INTEGER DEFAULT 0, -- 0=New, 1=Learning, 2=Mastered
    last_reviewed TIMESTAMP,
    next_review TIMESTAMP,
    review_count INTEGER DEFAULT 0,
    correct_count INTEGER DEFAULT 0,
    wrong_count INTEGER DEFAULT 0,
    familiarity REAL DEFAULT 0.0,
    FOREIGN KEY (word_id) REFERENCES words (id)
);
"""

CREATE_STUDY_PLAN_TABLE = """
CREATE TABLE IF NOT EXISTS study_plan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_name TEXT NOT NULL,
    daily_goal INTEGER DEFAULT 20,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);
"""

CREATE_QUIZ_RECORDS_TABLE = """
CREATE TABLE IF NOT EXISTS quiz_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_type TEXT,
    total_questions INTEGER,
    correct_answers INTEGER,
    quiz_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duration INTEGER
);
"""

INIT_STATEMENTS = [
    CREATE_LIBRARIES_TABLE,
    INSERT_DEFAULT_LIBRARY,
    CREATE_WORDS_TABLE,
    CREATE_USER_PROGRESS_TABLE,
    CREATE_STUDY_PLAN_TABLE,
    CREATE_QUIZ_RECORDS_TABLE
]
