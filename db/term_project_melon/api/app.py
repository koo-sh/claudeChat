"""
멜론 텀프로젝트 API (Python Flask + pymysql)

화면 ① 홈          : GET  /api/home/new-songs, GET /api/home/chart, GET /api/users/<id>/now-playing
화면 ② 재생목록    : GET/POST /api/users/<id>/queue, PATCH /api/users/<id>/queue/current,
                     DELETE /api/users/<id>/queue/<position>
화면 ③ 좋아요 > 곡 : GET/POST /api/users/<id>/likes/songs, DELETE /api/users/<id>/likes/songs/<song_id>
재생 기록         : POST /api/users/<id>/plays  (곡을 한 번 들을 때마다 play_history 1행 → 많이 들은/잊고 지낸의 원본)

- SQL 은 sql/03_view_queries.sql 의 쿼리를 그대로 옮긴 것이에요. @변수 자리에 %s (입력값) 가 들어가요.
- 곡 정보 + 아티스트 이름은 VIEW song_info 에서 가져와요.
- 실행: python app.py  →  http://localhost:5000
"""
from datetime import date, datetime
from decimal import Decimal

from flask import Flask, jsonify, request

import db

app = Flask(__name__)
app.json.ensure_ascii = False      # 한글이 \uXXXX 로 깨지지 않게
app.json.sort_keys = False         # JSON 키 순서를 코드에 쓴 순서대로

# 팀 결정사항 (docs/03_결정사항.md)
MIN_PLAY_COUNT = 3        # #13  "많이 들은" = 3회 이상 들은 곡
FORGOTTEN_DAYS = 30       # #7   "잊고 지낸" = 30일 넘게 안 들은 곡
DEFAULT_NEW_SONGS = 8     # 홈 최신음악 기본 개수
DEFAULT_CHART_SIZE = 10   # 홈 멜론차트 기본 개수


# ---------------------------------------------------------------------
# 공통 도우미
# ---------------------------------------------------------------------
def clean(row):
    """DB 에서 받은 dict 의 날짜/Decimal 값을 JSON 으로 보낼 수 있는 형태로 바꿔요."""
    out = {}
    for k, v in row.items():
        if isinstance(v, datetime):
            v = v.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(v, date):
            v = v.strftime("%Y-%m-%d")
        elif isinstance(v, Decimal):
            v = int(v) if v == int(v) else float(v)
        out[k] = v
    return out


def error(message, status):
    return jsonify({"error": message}), status


def user_exists(user_id):
    return db.fetch_one("SELECT user_id FROM users WHERE user_id = %s", (user_id,)) is not None


def song_exists(song_id):
    return db.fetch_one("SELECT song_id FROM song WHERE song_id = %s", (song_id,)) is not None


def now_param():
    """테스트용 ?now=YYYY-MM-DD HH:MM:SS (생략하면 None → SQL 에서 NOW() 사용)."""
    return request.args.get("now") or None


def rank_change_label(change):
    """rank_change 숫자 → 화면 표시 ('-', '▲1', '▼2', 'NEW')"""
    if change is None:
        return "NEW"
    if change > 0:
        return f"▲{change}"
    if change < 0:
        return f"▼{-change}"
    return "-"


@app.errorhandler(404)
def not_found(_):
    return error("not found", 404)


@app.errorhandler(400)
def bad_request(e):
    return error(getattr(e, "description", "bad request"), 400)


# =====================================================================
# ① 홈
# =====================================================================
@app.get("/api/home/new-songs")
def home_new_songs():
    """최신음악 (탭: 전체 / 국내 / 해외)  ?region=국내|해외&limit=8"""
    region = request.args.get("region") or None
    if region not in (None, "국내", "해외"):
        return error("region 은 '국내' 또는 '해외' 만 가능해요", 400)
    limit = request.args.get("limit", DEFAULT_NEW_SONGS, type=int)

    rows = db.fetch_all(
        """
        SELECT si.song_id, si.song_title, si.artists, si.cover_url, si.release_date, si.region
        FROM song_info si
        WHERE (%s IS NULL OR si.region = %s)
        ORDER BY si.release_date DESC, si.song_id
        LIMIT %s
        """,
        (region, region, limit),
    )
    return jsonify({"region": region or "전체", "count": len(rows), "songs": [clean(r) for r in rows]})


@app.get("/api/home/chart")
def home_chart():
    """멜론차트 (가장 최근 기준 시각 + 순위 변동)  ?chart_id=1&limit=10"""
    chart_id = request.args.get("chart_id", 1, type=int)
    limit = request.args.get("limit", DEFAULT_CHART_SIZE, type=int)
    now = now_param()

    chart = db.fetch_one("SELECT chart_id, chart_name FROM chart WHERE chart_id = %s", (chart_id,))
    if chart is None:
        return error("없는 chart_id 예요", 404)

    # 가장 최근 기준 시각 (cur_time) 과 그 직전 시각 (prev_time)
    t = db.fetch_one(
        """
        SELECT MAX(chart_time) AS cur_time
        FROM chart_entry
        WHERE chart_id = %s AND chart_time <= COALESCE(%s, NOW())
        """,
        (chart_id, now),
    )
    cur_time = t["cur_time"] if t else None
    if cur_time is None:
        return jsonify({**chart, "base_time": None, "items": []})

    p = db.fetch_one(
        "SELECT MAX(chart_time) AS prev_time FROM chart_entry WHERE chart_id = %s AND chart_time < %s",
        (chart_id, cur_time),
    )
    prev_time = p["prev_time"] if p else None

    rows = db.fetch_all(
        """
        SELECT cur.rank_no,
               prev.rank_no - cur.rank_no AS rank_change,
               si.song_id, si.song_title, si.artists, si.cover_url
        FROM chart_entry cur
        LEFT JOIN chart_entry prev
               ON prev.chart_id   = cur.chart_id
              AND prev.chart_time = %s
              AND prev.song_id    = cur.song_id
        JOIN song_info si ON si.song_id = cur.song_id
        WHERE cur.chart_id   = %s
          AND cur.chart_time = %s
        ORDER BY cur.rank_no
        LIMIT %s
        """,
        (prev_time, chart_id, cur_time, limit),
    )
    items = []
    for r in rows:
        r = clean(r)
        r["change_label"] = rank_change_label(r["rank_change"])
        items.append(r)

    return jsonify({
        **chart,
        "base_time": clean({"t": cur_time})["t"],
        "prev_time": clean({"t": prev_time})["t"],
        "items": items,
    })


@app.get("/api/users/<int:user_id>/now-playing")
def now_playing(user_id):
    """미니플레이어: 지금 재생 중인 곡"""
    if not user_exists(user_id):
        return error("없는 user_id 예요", 404)
    row = db.fetch_one(
        """
        SELECT q.position, si.song_id, si.song_title, si.artists, si.cover_url, si.duration_sec
        FROM play_queue q
        JOIN song_info si ON si.song_id = q.song_id
        WHERE q.user_id = %s AND q.is_current = 1
        """,
        (user_id,),
    )
    return jsonify({"user_id": user_id, "now_playing": clean(row) if row else None})


# =====================================================================
# ② 재생목록
# =====================================================================
@app.get("/api/users/<int:user_id>/queue")
def get_queue(user_id):
    """재생목록: 곡 수 + 곡 리스트 (내설정순)"""
    if not user_exists(user_id):
        return error("없는 user_id 예요", 404)
    rows = db.fetch_all(
        """
        SELECT q.position, q.is_current, si.song_id, si.song_title, si.artists, si.cover_url, q.added_at
        FROM play_queue q
        JOIN song_info si ON si.song_id = q.song_id
        WHERE q.user_id = %s
        ORDER BY q.position
        """,
        (user_id,),
    )
    return jsonify({"user_id": user_id, "song_count": len(rows), "songs": [clean(r) for r in rows]})


@app.post("/api/users/<int:user_id>/queue")
def add_to_queue(user_id):
    """재생목록 맨 뒤에 곡 추가  body: {"song_id": 4}"""
    if not user_exists(user_id):
        return error("없는 user_id 예요", 404)
    body = request.get_json(silent=True) or {}
    song_id = body.get("song_id")
    if not isinstance(song_id, int):
        return error("song_id (정수) 가 필요해요", 400)
    if not song_exists(song_id):
        return error("없는 song_id 예요", 404)

    with db.transaction() as cur:
        cur.execute("SELECT COALESCE(MAX(position), 0) AS last_pos FROM play_queue WHERE user_id = %s", (user_id,))
        last_pos = cur.fetchone()["last_pos"]
        position = last_pos + 1
        is_current = 1 if last_pos == 0 else 0      # 비어 있던 재생목록이면 바로 재생 곡으로
        cur.execute(
            "INSERT INTO play_queue (user_id, position, song_id, is_current) VALUES (%s, %s, %s, %s)",
            (user_id, position, song_id, is_current),
        )

    row = db.fetch_one(
        """
        SELECT q.position, q.is_current, si.song_id, si.song_title, si.artists, q.added_at
        FROM play_queue q JOIN song_info si ON si.song_id = q.song_id
        WHERE q.user_id = %s AND q.position = %s
        """,
        (user_id, position),
    )
    return jsonify({"user_id": user_id, "added": clean(row)}), 201


@app.patch("/api/users/<int:user_id>/queue/current")
def set_current(user_id):
    """현재 재생 곡 바꾸기  body: {"position": 1}  (사용자당 is_current=1 은 1곡만 → 트랜잭션으로 보장)"""
    if not user_exists(user_id):
        return error("없는 user_id 예요", 404)
    body = request.get_json(silent=True) or {}
    position = body.get("position")
    if not isinstance(position, int):
        return error("position (정수) 이 필요해요", 400)

    with db.transaction() as cur:
        cur.execute("SELECT song_id FROM play_queue WHERE user_id = %s AND position = %s", (user_id, position))
        if cur.fetchone() is None:
            return error("재생목록에 그 position 이 없어요", 404)
        cur.execute("UPDATE play_queue SET is_current = 0 WHERE user_id = %s", (user_id,))
        cur.execute("UPDATE play_queue SET is_current = 1 WHERE user_id = %s AND position = %s", (user_id, position))

    return now_playing(user_id)


@app.delete("/api/users/<int:user_id>/queue/<int:position>")
def remove_from_queue(user_id, position):
    """재생목록에서 곡 빼기. 뒤 곡들의 position 을 한 칸씩 당겨서 빈 번호가 없게 함"""
    if not user_exists(user_id):
        return error("없는 user_id 예요", 404)

    with db.transaction() as cur:
        cur.execute("SELECT song_id, is_current FROM play_queue WHERE user_id = %s AND position = %s", (user_id, position))
        target = cur.fetchone()
        if target is None:
            return error("재생목록에 그 position 이 없어요", 404)
        cur.execute("DELETE FROM play_queue WHERE user_id = %s AND position = %s", (user_id, position))
        # 뒤 번호 당기기 (position 이 PK 라서 작은 번호부터 차례로 바꿔야 충돌이 없음)
        cur.execute(
            "UPDATE play_queue SET position = position - 1 WHERE user_id = %s AND position > %s ORDER BY position",
            (user_id, position),
        )
        # 재생 중이던 곡을 지웠으면 같은 자리(다음 곡) 또는 마지막 곡을 재생 곡으로
        if target["is_current"]:
            cur.execute(
                """
                UPDATE play_queue SET is_current = 1
                WHERE user_id = %s AND position = (
                    SELECT p FROM (
                        SELECT COALESCE(MIN(CASE WHEN position >= %s THEN position END), MAX(position)) AS p
                        FROM play_queue WHERE user_id = %s
                    ) AS t
                )
                """,
                (user_id, position, user_id),
            )

    return jsonify({"user_id": user_id, "deleted_position": position, "deleted_song_id": target["song_id"]})


# =====================================================================
# ③ 음악서랍 > 좋아요 > 곡
# =====================================================================
@app.get("/api/users/<int:user_id>/likes/songs")
def liked_songs(user_id):
    """좋아요 곡 목록  ?filter=all(최신순) | most(많이 들은) | forgotten(잊고 지낸)"""
    if not user_exists(user_id):
        return error("없는 user_id 예요", 404)
    flt = request.args.get("filter", "all")
    now = now_param()

    if flt == "all":
        rows = db.fetch_all(
            """
            SELECT si.song_id, si.song_title, si.artists, si.cover_url, l.liked_at
            FROM song_like l
            JOIN song_info si ON si.song_id = l.song_id
            WHERE l.user_id = %s
            ORDER BY l.liked_at DESC
            """,
            (user_id,),
        )
    elif flt == "most":
        rows = db.fetch_all(
            """
            SELECT si.song_id, si.song_title, si.artists, si.cover_url,
                   COUNT(h.history_id) AS play_count
            FROM song_like l
            JOIN song_info si ON si.song_id = l.song_id
            JOIN play_history h ON h.user_id = l.user_id AND h.song_id = l.song_id
            WHERE l.user_id = %s
            GROUP BY si.song_id, si.song_title, si.artists, si.cover_url
            HAVING play_count >= %s
            ORDER BY play_count DESC, si.song_id
            """,
            (user_id, MIN_PLAY_COUNT),
        )
    elif flt == "forgotten":
        rows = db.fetch_all(
            """
            SELECT si.song_id, si.song_title, si.artists, si.cover_url,
                   MAX(h.played_at) AS last_played_at
            FROM song_like l
            JOIN song_info si ON si.song_id = l.song_id
            LEFT JOIN play_history h ON h.user_id = l.user_id AND h.song_id = l.song_id
            WHERE l.user_id = %s
            GROUP BY si.song_id, si.song_title, si.artists, si.cover_url
            HAVING last_played_at IS NULL
                OR last_played_at < DATE_SUB(COALESCE(%s, NOW()), INTERVAL %s DAY)
            ORDER BY last_played_at
            """,
            (user_id, now, FORGOTTEN_DAYS),
        )
    else:
        return error("filter 는 all / most / forgotten 중 하나예요", 400)

    return jsonify({"user_id": user_id, "filter": flt, "count": len(rows), "songs": [clean(r) for r in rows]})


@app.post("/api/users/<int:user_id>/likes/songs")
def like_song(user_id):
    """좋아요  body: {"song_id": 3}"""
    if not user_exists(user_id):
        return error("없는 user_id 예요", 404)
    body = request.get_json(silent=True) or {}
    song_id = body.get("song_id")
    if not isinstance(song_id, int):
        return error("song_id (정수) 가 필요해요", 400)
    if not song_exists(song_id):
        return error("없는 song_id 예요", 404)
    if db.fetch_one("SELECT 1 FROM song_like WHERE user_id = %s AND song_id = %s", (user_id, song_id)):
        return error("이미 좋아요한 곡이에요", 409)      # PK (user_id, song_id) 중복

    with db.transaction() as cur:
        cur.execute("INSERT INTO song_like (user_id, song_id) VALUES (%s, %s)", (user_id, song_id))

    row = db.fetch_one(
        """
        SELECT si.song_id, si.song_title, si.artists, l.liked_at
        FROM song_like l JOIN song_info si ON si.song_id = l.song_id
        WHERE l.user_id = %s AND l.song_id = %s
        """,
        (user_id, song_id),
    )
    return jsonify({"user_id": user_id, "liked": clean(row)}), 201


@app.delete("/api/users/<int:user_id>/likes/songs/<int:song_id>")
def unlike_song(user_id, song_id):
    """좋아요 취소"""
    if not user_exists(user_id):
        return error("없는 user_id 예요", 404)
    with db.transaction() as cur:
        cur.execute("DELETE FROM song_like WHERE user_id = %s AND song_id = %s", (user_id, song_id))
        deleted = cur.rowcount
    if deleted == 0:
        return error("좋아요하지 않은 곡이에요", 404)
    return jsonify({"user_id": user_id, "song_id": song_id, "unliked": True})


# =====================================================================
# 재생 기록 (play_history 에 쌓기) → "많이 들은" / "잊고 지낸" 의 원본 데이터
# =====================================================================
@app.post("/api/users/<int:user_id>/plays")
def record_play(user_id):
    """곡을 한 번 들었을 때 재생 기록 1행 추가  body: {"song_id": 1}"""
    if not user_exists(user_id):
        return error("없는 user_id 예요", 404)
    body = request.get_json(silent=True) or {}
    song_id = body.get("song_id")
    if not isinstance(song_id, int):
        return error("song_id (정수) 가 필요해요", 400)
    if not song_exists(song_id):
        return error("없는 song_id 예요", 404)

    with db.transaction() as cur:
        cur.execute("INSERT INTO play_history (user_id, song_id) VALUES (%s, %s)", (user_id, song_id))
        history_id = cur.lastrowid          # AUTO_INCREMENT 로 매겨진 번호

    # 방금 쌓인 기록까지 포함해서, 이 사용자가 이 곡을 몇 번 / 마지막으로 언제 들었는지
    stats = db.fetch_one(
        """
        SELECT COUNT(*) AS play_count, MAX(played_at) AS last_played_at
        FROM play_history
        WHERE user_id = %s AND song_id = %s
        """,
        (user_id, song_id),
    )
    return jsonify({
        "user_id": user_id,
        "song_id": song_id,
        "history_id": history_id,
        **clean(stats),
    }), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
