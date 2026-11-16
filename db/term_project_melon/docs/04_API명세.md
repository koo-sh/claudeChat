# 04. API 명세 (초안)

> 상태: **API 목록 초안**. 응답 형식과 JSON 예시는 Phase 2~3에서 B, C가 구현하면서 Postman 캡처로 채워요.
> 쿼리는 [`../sql/03_view_queries.sql`](../sql/03_view_queries.sql)에 이미 있어요. API는 쿼리의 `@변수` 자리(`@user_id`, `@region`, `@chart_id`)에 입력값을 넣어 실행하고, 결과를 JSON으로 바꿔 주면 돼요.

- 서버: Python **Flask** + **pymysql**
- 주소: `http://localhost:5000`
- 로그인은 구현하지 않고, URL에 `user_id`를 넣어서 사용자를 구분해요(과제 범위 단순화).

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
