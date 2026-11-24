-- =====================================================================
-- 멜론 텀프로젝트: 기초 테이블 (MySQL 8.x)
--   화면 ① 홈(최신음악, 멜론차트)  ② 재생목록  ③ 음악서랍 > 좋아요 > 곡
--   설계 근거: docs/02_DB설계.md
--   실행: MySQL Workbench에서 이 파일 전체 실행 → 02_sample_data.sql 실행
--   ※ play_queue 의 CHECK 제약은 MySQL 8.0.16 이상에서만 실제로 검사됨
-- =====================================================================

DROP DATABASE IF EXISTS melon;
CREATE DATABASE melon;
USE melon;

-- ---------------------------------------------------------------------
-- 1. users : 앱 사용자
--    (user 는 MySQL 시스템 테이블 이름과 헷갈려서 users 로 함)
-- ---------------------------------------------------------------------
CREATE TABLE users (
    user_id     INT          NOT NULL AUTO_INCREMENT,
    nickname    VARCHAR(50)  NOT NULL,
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id)
);

-- ---------------------------------------------------------------------
-- 2. artist : 아티스트 (가수, 그룹)
--    화면 표기 "RESCENE (리센느)" 그대로 artist_name 에 저장
-- ---------------------------------------------------------------------
CREATE TABLE artist (
    artist_id    INT           NOT NULL AUTO_INCREMENT,
    artist_name  VARCHAR(100)  NOT NULL,
    PRIMARY KEY (artist_id)
);

-- ---------------------------------------------------------------------
-- 3. song : 곡
--    커버, 발매일, 국내/해외도 곡 단위로 저장 (앨범 화면이 과제 범위 밖이라 album 테이블은 두지 않음)
--    모든 컬럼이 song_id 하나에만 종속 → 3NF
-- ---------------------------------------------------------------------
CREATE TABLE song (
    song_id       INT           NOT NULL AUTO_INCREMENT,
    song_title    VARCHAR(200)  NOT NULL,
    cover_url     VARCHAR(500)  NOT NULL,          -- 커버 이미지
    release_date  DATE          NOT NULL,          -- 홈 > 최신음악 정렬 기준
    region        ENUM('국내', '해외') NOT NULL,   -- 홈 > 최신음악 국내/해외 탭
    duration_sec  INT           NOT NULL,          -- 재생 시간(초)
    PRIMARY KEY (song_id)
);

-- ---------------------------------------------------------------------
-- 4. song_artist : 곡 ↔ 아티스트 (N:M)
--    "NEON — A20, A20 LITE" 처럼 한 곡에 아티스트 여러 명 → 1NF
--    artist_order : 화면에 표시할 순서 (1 = 첫 번째)
-- ---------------------------------------------------------------------
CREATE TABLE song_artist (
    song_id       INT      NOT NULL,
    artist_id     INT      NOT NULL,
    artist_order  TINYINT  NOT NULL DEFAULT 1,
    PRIMARY KEY (song_id, artist_id),
    FOREIGN KEY (song_id)   REFERENCES song (song_id)     ON DELETE CASCADE,
    FOREIGN KEY (artist_id) REFERENCES artist (artist_id) ON DELETE CASCADE
);

-- ---------------------------------------------------------------------
-- 5. chart : 차트 종류 (TOP100, HOT100, 비오고 흐린 날 ...)
-- ---------------------------------------------------------------------
CREATE TABLE chart (
    chart_id    INT          NOT NULL AUTO_INCREMENT,
    chart_name  VARCHAR(50)  NOT NULL,
    PRIMARY KEY (chart_id),
    UNIQUE (chart_name)
);

-- ---------------------------------------------------------------------
-- 6. chart_entry : 시각별 차트 순위 ("오늘 23:00 기준")
--    순위 변동은 저장하지 않고 직전 chart_time 과 비교해서 계산
-- ---------------------------------------------------------------------
CREATE TABLE chart_entry (
    chart_id    INT       NOT NULL,
    chart_time  DATETIME  NOT NULL,                -- 기준 시각 (매 정시)
    rank_no     INT       NOT NULL,                -- rank 는 MySQL 8 예약어라 rank_no
    song_id     INT       NOT NULL,
    PRIMARY KEY (chart_id, chart_time, rank_no),
    UNIQUE (chart_id, chart_time, song_id),        -- 같은 시각 같은 차트에 같은 곡 두 번 X
    FOREIGN KEY (chart_id) REFERENCES chart (chart_id),
    FOREIGN KEY (song_id)  REFERENCES song (song_id)
);

-- ---------------------------------------------------------------------
-- 7. play_queue : 재생목록 (지금 듣는 곡 대기열)
--    position   : "내설정순" 순서 (1, 2, 3 ...)
--    is_current : 지금 재생 중인 곡이면 1, 아니면 NULL  (0 은 쓰지 않음)
--      - CHECK (is_current = 1)        → 넣을 수 있는 값은 1 또는 NULL 뿐
--      - UNIQUE (user_id, is_current)  → 사용자당 1 은 한 행만 가능
--                                        NULL 은 UNIQUE 에서 중복으로 치지 않아서 여러 행 가능
--      → "사용자당 재생 중인 곡은 1곡" 을 API 가 아니라 DB 가 보장
--    같은 곡을 두 번 넣을 수 있어서 PK 는 (user_id, position)
-- ---------------------------------------------------------------------
CREATE TABLE play_queue (
    user_id     INT         NOT NULL,
    position    INT         NOT NULL,
    song_id     INT         NOT NULL,
    is_current  TINYINT(1)  NULL DEFAULT NULL,
    added_at    DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, position),
    UNIQUE KEY uq_one_current (user_id, is_current),
    CONSTRAINT chk_is_current CHECK (is_current = 1),
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (song_id) REFERENCES song (song_id)
);

-- ---------------------------------------------------------------------
-- 8. song_like : 곡 좋아요
--    liked_at : "최신순" 정렬 기준
-- ---------------------------------------------------------------------
CREATE TABLE song_like (
    user_id   INT       NOT NULL,
    song_id   INT       NOT NULL,
    liked_at  DATETIME  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, song_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (song_id) REFERENCES song (song_id)
);

-- ---------------------------------------------------------------------
-- 9. play_history : 재생 기록 (한 번 들을 때마다 1행)
--    좋아요 > "많이 들은"(COUNT), "잊고 지낸"(MAX(played_at)) 계산용
-- ---------------------------------------------------------------------
CREATE TABLE play_history (
    history_id  INT       NOT NULL AUTO_INCREMENT,
    user_id     INT       NOT NULL,
    song_id     INT       NOT NULL,
    played_at   DATETIME  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (history_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (song_id) REFERENCES song (song_id),
    INDEX idx_history_user_song (user_id, song_id, played_at)
);

-- =====================================================================
-- VIEW. song_info : 곡 정보 + 아티스트 이름을 한 줄로 합친 것
--   저장은 1NF로 나눠서(song_artist), 화면에 보여줄 때만 "A20, A20 LITE" 처럼 합침
--   VIEW 는 데이터를 따로 저장하지 않음 → 테이블들은 그대로 3NF
--   화면별 쿼리(03_view_queries.sql)는 모두 이 VIEW 를 JOIN 해서 사용
-- =====================================================================
CREATE VIEW song_info AS
SELECT s.song_id,
       s.song_title,
       GROUP_CONCAT(ar.artist_name ORDER BY sa.artist_order SEPARATOR ', ') AS artists,
       s.cover_url,
       s.release_date,
       s.region,
       s.duration_sec
FROM song s
JOIN song_artist sa ON sa.song_id   = s.song_id
JOIN artist ar      ON ar.artist_id = sa.artist_id
GROUP BY s.song_id, s.song_title, s.cover_url, s.release_date, s.region, s.duration_sec;
