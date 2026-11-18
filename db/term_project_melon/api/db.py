"""
db.py : MySQL 연결 (pymysql)

- config.py 의 DB 설정을 읽어서 연결을 만들어요.
- 결과는 dict 로 받아요 (DictCursor) → 그대로 JSON 으로 바꾸기 쉬움
- 사용법
    rows = fetch_all("SELECT ... WHERE user_id = %s", (user_id,))
    row  = fetch_one("SELECT COUNT(*) AS n FROM ...", ())
    with transaction() as cur:          # 쓰기(INSERT/UPDATE/DELETE) 는 트랜잭션 안에서
        cur.execute("INSERT ...", (...))
"""
from contextlib import contextmanager

import pymysql
import pymysql.cursors

try:
    import config
except ImportError as e:  # config.example.py 를 복사해서 config.py 를 만들어야 함
    raise SystemExit("config.py 가 없어요. config.example.py 를 복사해서 config.py 를 만들고 비밀번호를 적어 주세요.") from e


def connect():
    """새 DB 연결을 돌려줘요 (autocommit 꺼짐 → 쓰기는 commit 필요)."""
    return pymysql.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )


def fetch_all(sql, params=()):
    """SELECT 결과 전체를 list[dict] 로."""
    conn = connect()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()
    finally:
        conn.close()


def fetch_one(sql, params=()):
    """SELECT 결과 첫 행을 dict 로 (없으면 None)."""
    conn = connect()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchone()
    finally:
        conn.close()


@contextmanager
def transaction():
    """
    쓰기 작업용. with 블록이 정상 종료되면 commit, 예외가 나면 rollback.
        with transaction() as cur:
            cur.execute(...)
            cur.execute(...)
    """
    conn = connect()
    try:
        with conn.cursor() as cur:
            yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
