# 04. API 명세 (초안)

> 상태: **11개 모두 구현 완료** → [`../api/app.py`](../api/app.py). 실행 방법은 [`../api/README.md`](../api/README.md), Postman 요청 모음은 [`../api/postman_collection.json`](../api/postman_collection.json).
> API별 입력값과 실제 JSON 응답은 **보고서 4.2절**(`report/보고서.docx`)에 있어요.
> 쿼리는 [`../sql/03_view_queries.sql`](../sql/03_view_queries.sql)에 이미 있어요. API는 쿼리의 `@변수` 자리(`@user_id`, `@region`, `@chart_id`)에 입력값을 넣어 실행하고, 결과를 JSON으로 바꿔 주면 돼요.

- 서버: Python **Flask** + **pymysql**
- 주소: `http://localhost:5000`
- 로그인은 구현하지 않고, URL에 `user_id`를 넣어서 사용자를 구분해요(과제 범위 단순화).

## API 목록

| # | 화면 | Method | URL | 설명 | 담당 | 구현 |
|---|---|---|---|---|---|---|
| 1 | 홈 | GET | `/api/home/new-songs?region=&limit=` | 최신음악 (region: 생략=전체, `국내`, `해외`) | B | ✅ |
| 2 | 홈 | GET | `/api/home/chart?chart_id=&limit=` | 멜론차트 최신 기준 시각 + 순위 변동 | B | ✅ |
| 3 | 홈, 재생목록 | GET | `/api/users/<user_id>/now-playing` | 미니플레이어 (현재 재생 곡) | B | ✅ |
| 4 | 재생목록 | GET | `/api/users/<user_id>/queue` | 곡 수 + 곡 리스트 (내설정순) | C | ✅ |
| 5 | 재생목록 | POST | `/api/users/<user_id>/queue` | 곡을 재생목록 맨 뒤에 추가 `{"song_id": 4}` | C | ✅ |
| 6 | 재생목록 | PATCH | `/api/users/<user_id>/queue/current` | 현재 재생 곡 바꾸기 `{"position": 1}` | C | ✅ |
| 7 | 재생목록 | DELETE | `/api/users/<user_id>/queue/<position>` | 재생목록에서 곡 빼기 | C | ✅ |
| 8 | 좋아요 | GET | `/api/users/<user_id>/likes/songs?filter=` | filter: `all`(최신순), `most`(많이 들은), `forgotten`(잊고 지낸) | C | ✅ |
| 9 | 좋아요 | POST | `/api/users/<user_id>/likes/songs` | 좋아요 `{"song_id": 3}` | C | ✅ |
| 10 | 좋아요 | DELETE | `/api/users/<user_id>/likes/songs/<song_id>` | 좋아요 취소 | C | ✅ |
| 11 | 재생목록·좋아요 | POST | `/api/users/<user_id>/plays` | 재생 기록 추가 `{"song_id": 2}`. 곡을 한 번 들을 때마다 play_history 1행 → "많이 들은", "잊고 지낸"의 원본 | C | ✅ |

- 조회 5개 + 쓰기 6개. 에러는 `{"error": "이유"}`와 상태 코드(400 잘못된 입력, 404 없음, 409 중복)로 돌려줘요.
- 테스트용으로 `?now=2026-11-15 23:30:00`을 붙이면 차트와 "잊고 지낸"의 기준 시각을 샘플 데이터에 맞춰 고정할 수 있어요.

**발표 시연 추천 흐름 (11번)**: `8. 많이 들은` 조회(With 1곡) → `11. 재생 기록 추가` `{"song_id": 2}` 3번 → `8. 많이 들은` 다시 조회(With, LOVE ATTACK 2곡). 기록이 쌓이면 화면이 바뀌는 걸 보여줄 수 있어요.
