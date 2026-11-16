-- =====================================================================
-- 화면별 SELECT 쿼리 (API 가 이 쿼리를 그대로 사용할 예정)
--   @변수 = API 입력값 자리. Workbench 에서 SET 값만 바꿔서 테스트하면 됨
--   @now  = "지금 시각". 샘플 데이터 기준으로 고정해 두었음 (API 에서는 NOW())
--   song_info = 곡 정보 + 아티스트 이름을 합친 VIEW (01_schema.sql 맨 끝)
-- =====================================================================
USE melon;

SET @user_id  = 1;
SET @now      = '2026-11-15 23:30:00';

-- =====================================================================
-- ① 홈 - 최신음악   (탭: 전체 / 국내 / 해외)
--   @region = NULL 이면 전체, '국내' / '해외' 면 해당 탭
-- =====================================================================
SET @region = NULL;

SELECT si.song_id, si.song_title, si.artists, si.cover_url, si.release_date, si.region
FROM song_info si
WHERE (@region IS NULL OR si.region = @region)
ORDER BY si.release_date DESC, si.song_id
LIMIT 8;

-- =====================================================================
-- ① 홈 - 멜론차트   (가장 최근 기준 시각 + 순위 변동)
--   rank_change : 양수 = 상승, 음수 = 하락, 0 = 변동 없음('-'), NULL = 신규(NEW)
--   같은 테이블을 cur(현재) / prev(직전 시각) 로 두 번 불러서 같은 곡끼리 LEFT JOIN
-- =====================================================================
SET @chart_id = 1;   -- 1 TOP100, 2 HOT100, 3 비오고 흐린 날

-- 가장 최근 기준 시각과 그 직전 시각
SET @cur_time  = (SELECT MAX(chart_time) FROM chart_entry
                  WHERE chart_id = @chart_id AND chart_time <= @now);
SET @prev_time = (SELECT MAX(chart_time) FROM chart_entry
                  WHERE chart_id = @chart_id AND chart_time < @cur_time);

SELECT cur.chart_time              AS base_time,
       cur.rank_no,
       prev.rank_no - cur.rank_no  AS rank_change,
       si.song_id, si.song_title, si.artists, si.cover_url
FROM chart_entry cur
LEFT JOIN chart_entry prev
       ON prev.chart_id   = cur.chart_id
      AND prev.chart_time = @prev_time
      AND prev.song_id    = cur.song_id
JOIN song_info si ON si.song_id = cur.song_id
WHERE cur.chart_id   = @chart_id
  AND cur.chart_time = @cur_time
ORDER BY cur.rank_no;

-- =====================================================================
-- ① 홈 / ② 재생목록 - 미니플레이어 (지금 재생 중인 곡)
-- =====================================================================
SELECT q.position, si.song_id, si.song_title, si.artists, si.cover_url
FROM play_queue q
JOIN song_info si ON si.song_id = q.song_id
WHERE q.user_id = @user_id
  AND q.is_current = 1;

-- =====================================================================
-- ② 재생목록 - 곡 수 ("2곡")
-- =====================================================================
SELECT COUNT(*) AS song_count
FROM play_queue
WHERE user_id = @user_id;

-- =====================================================================
-- ② 재생목록 - 곡 리스트 (내설정순 = position 순)
-- =====================================================================
SELECT q.position, q.is_current, si.song_id, si.song_title, si.artists, si.cover_url
FROM play_queue q
JOIN song_info si ON si.song_id = q.song_id
WHERE q.user_id = @user_id
ORDER BY q.position;

-- =====================================================================
-- ③ 좋아요 > 곡 - 전체 (최신순 = 좋아요 누른 시각 최신순)
-- =====================================================================
SELECT l.liked_at, si.song_id, si.song_title, si.artists, si.cover_url
FROM song_like l
JOIN song_info si ON si.song_id = l.song_id
WHERE l.user_id = @user_id
ORDER BY l.liked_at DESC;

-- =====================================================================
-- ③ 좋아요 > 곡 - 많이 들은 (재생 횟수 많은 순)
--   LEFT JOIN : 한 번도 안 들은 좋아요 곡도 0회로 나오게
-- =====================================================================
SELECT si.song_id, si.song_title, si.artists, si.cover_url,
       COUNT(h.history_id) AS play_count
FROM song_like l
JOIN song_info si ON si.song_id = l.song_id
LEFT JOIN play_history h
       ON h.user_id = l.user_id AND h.song_id = l.song_id
WHERE l.user_id = @user_id
GROUP BY si.song_id, si.song_title, si.artists, si.cover_url
ORDER BY play_count DESC, si.song_id;

-- =====================================================================
-- ③ 좋아요 > 곡 - 잊고 지낸 (좋아요했지만 30일 넘게 안 들었거나 한 번도 안 들은 곡)
--   HAVING : 묶은 뒤의 값(MAX)으로 거를 때는 WHERE 가 아니라 HAVING
-- =====================================================================
SELECT si.song_id, si.song_title, si.artists, si.cover_url,
       MAX(h.played_at) AS last_played_at
FROM song_like l
JOIN song_info si ON si.song_id = l.song_id
LEFT JOIN play_history h
       ON h.user_id = l.user_id AND h.song_id = l.song_id
WHERE l.user_id = @user_id
GROUP BY si.song_id, si.song_title, si.artists, si.cover_url
HAVING last_played_at IS NULL
    OR last_played_at < DATE_SUB(@now, INTERVAL 30 DAY)
ORDER BY last_played_at;
