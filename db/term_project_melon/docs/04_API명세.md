# 04. API 명세 (초안)

> 상태: **목록과 응답 형식 초안**. Phase 2~3에서 B, C가 실제로 구현하고, Postman 캡처로 채워요.
> 쿼리는 [`../sql/03_view_queries.sql`](../sql/03_view_queries.sql)에 이미 있어요. API는 그 쿼리를 실행해서 JSON으로 바꿔 주면 돼요.

- 서버: Python **Flask** + **pymysql**
- 주소: `http://localhost:5000`
- 로그인은 구현하지 않고, URL에 `user_id`를 넣어서 사용자를 구분해요(과제 범위 단순화).

## 공통 응답 형식

```json
{ "success": true, "data": { ... } }
```
```json
{ "success": false, "message": "user not found" }
```

## API 목록

| # | 화면 | Method | URL | 설명 | 담당 | 필수 |
|---|---|---|---|---|---|---|
| 1 | 홈 | GET | `/api/home/new-songs?region=&limit=` | 최신음악 (region: 생략=전체, `국내`, `해외`) | B | ✅ |
| 2 | 홈 | GET | `/api/home/chart?chart_id=&limit=` | 멜론차트 최신 기준 시각 + 순위 변동 | B | ✅ |
| 3 | 홈, 재생목록 | GET | `/api/users/<user_id>/now-playing` | 미니플레이어 (현재 재생 곡) | B | ✅ |
| 4 | 재생목록 | GET | `/api/users/<user_id>/queue` | 곡 수 + 곡 리스트 (내설정순) | C | ✅ |
| 5 | 재생목록 | POST | `/api/users/<user_id>/queue` | 곡을 재생목록 맨 뒤에 추가 `{"song_id": 4}` | C | ✅ |
| 6 | 재생목록 | PATCH | `/api/users/<user_id>/queue/current` | 현재 재생 곡 바꾸기 `{"position": 1}` | C | 선택 |
| 7 | 재생목록 | DELETE | `/api/users/<user_id>/queue/<position>` | 재생목록에서 곡 빼기 | C | 선택 |
| 8 | 좋아요 | GET | `/api/users/<user_id>/likes/songs?filter=` | filter: `all`(최신순), `most`(많이 들은), `forgotten`(잊고 지낸) | C | ✅ |
| 9 | 좋아요 | POST | `/api/users/<user_id>/likes/songs` | 좋아요 `{"song_id": 3}` | C | ✅ |
| 10 | 좋아요 | DELETE | `/api/users/<user_id>/likes/songs/<song_id>` | 좋아요 취소 | C | ✅ |

> 조회(GET)만 있으면 "DB를 읽기만 하는" 발표가 되기 때문에, 좋아요 추가/취소와 재생목록 추가처럼 **DB를 바꾸는 API**를 최소 2~3개 넣는 걸 추천해요.

## 응답 예시 (샘플 데이터로 실제 쿼리를 돌린 결과 기반)

### 2. `GET /api/home/chart?chart_id=1&limit=5`
```json
{
  "success": true,
  "data": {
    "chart_name": "TOP100",
    "base_time": "2026-11-15 23:00:00",
    "songs": [
      { "rank": 1, "rank_change": 0,    "song_id": 11, "title": "꿈꾸던 어른이 되었나요?", "artists": "머무르",        "cover_url": "https://example.com/cover/12.jpg" },
      { "rank": 2, "rank_change": 0,    "song_id": 1,  "title": "With",                   "artists": "RESCENE (리센느)", "cover_url": "https://example.com/cover/9.jpg" },
      { "rank": 3, "rank_change": 1,    "song_id": 3,  "title": "NEON",                   "artists": "A20, A20 LITE",  "cover_url": "https://example.com/cover/11.jpg" },
      { "rank": 4, "rank_change": -1,   "song_id": 5,  "title": "RAPLIFE",                "artists": "JJK",            "cover_url": "https://example.com/cover/2.jpg" },
      { "rank": 5, "rank_change": null, "song_id": 4,  "title": "사랑하면",               "artists": "KCM",            "cover_url": "https://example.com/cover/1.jpg" }
    ]
  }
}
```
`rank_change`: 양수 ▲, 음수 ▼, 0 = `-`, null = NEW

### 4. `GET /api/users/1/queue`
```json
{
  "success": true,
  "data": {
    "song_count": 2,
    "sort": "내설정순",
    "songs": [
      { "position": 1, "is_current": false, "song_id": 1, "title": "With", "artists": "RESCENE (리센느)", "cover_url": "https://example.com/cover/9.jpg" },
      { "position": 2, "is_current": true,  "song_id": 3, "title": "NEON", "artists": "A20, A20 LITE",  "cover_url": "https://example.com/cover/11.jpg" }
    ]
  }
}
```

### 8. `GET /api/users/1/likes/songs?filter=all`
```json
{
  "success": true,
  "data": {
    "filter": "all",
    "songs": [
      { "song_id": 1, "title": "With",        "artists": "RESCENE (리센느)", "cover_url": "https://example.com/cover/9.jpg",  "liked_at": "2026-11-14 20:00:00" },
      { "song_id": 2, "title": "LOVE ATTACK", "artists": "RESCENE (리센느)", "cover_url": "https://example.com/cover/10.jpg", "liked_at": "2025-03-10 18:30:00" }
    ]
  }
}
```

### 9. `POST /api/users/1/likes/songs`
요청 Body (raw JSON)
```json
{ "song_id": 3 }
```
응답
```json
{ "success": true, "data": { "user_id": 1, "song_id": 3, "liked_at": "2026-11-20 14:00:00" } }
```
실행 후 `SELECT * FROM song_like WHERE user_id = 1;`에 NEON이 추가되면 성공

## 구현 시 주의
- **SQL 인젝션 방지**: 쿼리에 문자열을 이어 붙이지 말고 `cursor.execute(sql, (user_id,))`처럼 파라미터 사용
- **is_current**: 현재 곡을 바꿀 때 기존 곡을 0으로 바꾸고 새 곡을 1로 바꾸기 (한 사용자에 1곡만 1)
- **재생목록 추가**: 새 position = `MAX(position) + 1` (비어 있으면 1)
- 좋아요 중복 추가 시 PK 충돌 → `"message": "already liked"`로 응답
