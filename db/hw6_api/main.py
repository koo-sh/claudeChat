# ============================================================
# HW6 - Krible '최신' tab: '내 관심사만 보기' API
#   GET /latest/my-interest?user_id=1
#   -> contents related to the topics and companies the user hearted (heart=1),
#      ordered by update_time DESC
#
# Run:
#   pip install fastapi uvicorn pymysql
#   uvicorn main:app --reload
#   open http://127.0.0.1:8000/docs  (or /latest/my-interest?user_id=1)
# ============================================================
import pymysql
from fastapi import FastAPI

DB_CONFIG = dict(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="",          # your MySQL password
    database="krible",
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor,
)

app = FastAPI(title="Krible API")


# ============================================================
# [SQL] Views (same as the workshop)
#   T_user_company_heart : user's hearted companies (latest state is heart=1)
#   T_user_topic_heart   : user's hearted topics   (latest state is heart=1)
# ============================================================
CREATE_USER_COMPANY_HEART = """
CREATE OR REPLACE VIEW T_user_company_heart AS
SELECT tuc.user_id, tuc.company_ticker
FROM T_user_company tuc
JOIN (
    SELECT user_id, company_ticker, max(update_time) update_time
    FROM T_user_company
    GROUP BY user_id, company_ticker
) a on tuc.user_id = a.user_id
and tuc.company_ticker = a.company_ticker
and tuc.update_time = a.update_time
WHERE tuc.heart = 1
"""

CREATE_USER_TOPIC_HEART = """
CREATE OR REPLACE VIEW T_user_topic_heart AS
SELECT tut.user_id, tut.topic_id
FROM T_user_topic tut
JOIN (
    SELECT user_id, topic_id, max(update_time) update_time
    FROM T_user_topic
    GROUP BY user_id, topic_id
) a on tut.user_id = a.user_id
and tut.topic_id = a.topic_id
and tut.update_time = a.update_time
WHERE tut.heart = 1
"""


# ============================================================
# [SQL] '내 관심사만 보기'
#   1. contents of hearted topics    -> T_user_topic_heart + T_content_topic
#   2. contents of hearted companies -> T_user_company_heart + T_content_company
#   3. UNION of 1 and 2 (a content is shown once even if it matches both)
#   4. content info: company1, topic1, topic2, title, author1 affiliation/name, time
#   5. update_time DESC
# ============================================================
MY_INTEREST_QUERY = """
SELECT tc.content_id,
       tc2.company_name company1, tt.topic_name topic1, tt2.topic_name topic2,
       tc.title, ta.affiliation, ta.author_name, tc.update_time
FROM T_content tc

LEFT JOIN T_content_company tcc on tc.content_id = tcc.content_id and tcc.orders = 1
LEFT JOIN T_company tc2 on tcc.company_ticker = tc2.company_ticker

LEFT JOIN T_content_topic tct on tc.content_id = tct.content_id and tct.orders = 1
LEFT JOIN T_topic tt on tct.topic_id = tt.topic_id

LEFT JOIN T_content_topic tct2 on tc.content_id = tct2.content_id and tct2.orders = 2
LEFT JOIN T_topic tt2 on tct2.topic_id = tt2.topic_id

LEFT JOIN T_content_author tca on tc.content_id = tca.content_id and tca.orders = 1
LEFT JOIN T_author ta on tca.author_id = ta.author_id

WHERE tc.content_id in (
    SELECT tct3.content_id
    FROM T_user_topic_heart tuth
    JOIN T_content_topic tct3 on tuth.topic_id = tct3.topic_id
    WHERE tuth.user_id = %(user_id)s

    UNION

    SELECT tcc3.content_id
    FROM T_user_company_heart tuch
    JOIN T_content_company tcc3 on tuch.company_ticker = tcc3.company_ticker
    WHERE tuch.user_id = %(user_id)s
)
ORDER BY tc.update_time DESC;
"""


def get_connection():
    return pymysql.connect(**DB_CONFIG)


@app.on_event("startup")
def create_views():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(CREATE_USER_COMPANY_HEART)
            cur.execute(CREATE_USER_TOPIC_HEART)
        conn.commit()
    finally:
        conn.close()


@app.get("/latest/my-interest")
def my_interest(user_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(MY_INTEREST_QUERY, {"user_id": user_id})
            rows = cur.fetchall()
    finally:
        conn.close()

    for row in rows:
        row["update_time"] = row["update_time"].strftime("%Y-%m-%d %H:%M:%S")
    return {"user_id": user_id, "count": len(rows), "contents": rows}
