# 데이터베이스 텀프로젝트: 멜론 앱 DB 설계 & API

멜론 음악 앱의 화면 3개를 골라, 그 화면을 그리는 데 필요한 **데이터베이스를 설계**하고 **API를 개발**하는 4인 팀 프로젝트예요.

> **팀원 읽는 순서**
> 1. 이 README (5분)
> 2. [`docs/00_진행계획.md`](docs/00_진행계획.md): 전체 일정, 역할, 할 일 (10분)
> 3. [`docs/03_결정사항.md`](docs/03_결정사항.md): **열린 결정사항에 의견 남기기**
> 4. [`docs/05_실행가이드.md`](docs/05_실행가이드.md): 내 PC에서 SQL 실행해 보기

## 과제 요구사항 (TP_DB.pdf 요약)

- 모바일 앱 1개 + 화면 3개 이상 선택
- 화면을 만들기 위한 **DB 구축** + 각 화면의 **API 개발**
- **발표 (10분 + Q&A 5분)**: 앱/화면 소개 → DB 설계 → API
- **보고서**: 앱/화면 소개, DB 설계(테이블, 쿼리, 데이터셋, ERD), API(입력값, JSON 출력)
- 사용 도구 (Week9_2): **Python, VSCode, Postman, MySQL**

## 일정

| 날짜 | 내용 |
|---|---|
| 11/15 (일) | 기초 작업 완료 (계획, 화면 분석, 기초 테이블, 샘플 데이터, 쿼리) |
| 11/16~17 | 킥오프: 역할 배정, 결정사항 확정, 각자 SQL 실행 확인 |
| 11/17~21 | DB 확정 + Flask API 개발 |
| 11/21~24 | Postman 테스트, API 명세 완성 |
| 11/24~28 | 보고서 + 슬라이드, 11/28(토) 최종 점검 |
| **11/29 (일) 23:59** | **슬라이드 + 보고서 사이버캠퍼스 제출** |
| 12/1 (화) 또는 12/7 (월) | 발표 (우리 조 발표일에만 참석, 12/1은 오프라인) |
| 발표 후 | 동료 평가 (비공개 설문, 최종 점수에 반영) |

## 선택한 화면

| # | 화면 | 범위 |
|---|---|---|
| 1 | 홈 | 최신음악(전체/국내/해외), 멜론차트(순위 변동 포함), 미니플레이어 |
| 2 | 재생목록 | 곡 수, 곡 리스트(내설정순), 현재 재생 곡 |
| 3 | 음악서랍 > 좋아요 > 곡 | 전체(최신순) / 많이 들은 / 잊고 지낸 |

<p>
  <img src="images/view1_home.jpg" width="220">
  <img src="images/view2_play_queue.jpg" width="220">
  <img src="images/view3_like_songs.jpg" width="220">
</p>

## 기초 테이블 (10개)

`users`, `artist`, `album`, `song`, `song_artist`, `chart`, `chart_entry`, `play_queue`, `song_like`, `play_history`
→ ERD와 설명은 [`docs/02_DB설계.md`](docs/02_DB설계.md)

## 문서와 파일

| 파일 | 내용 | 상태 |
|---|---|---|
| [`docs/00_진행계획.md`](docs/00_진행계획.md) | 일정, 역할(A~D), 단계별 할 일, 발표와 보고서 구성안 | ✅ |
| [`docs/01_화면분석.md`](docs/01_화면분석.md) | 화면별 필요 데이터 | ✅ |
| [`docs/02_DB설계.md`](docs/02_DB설계.md) | ERD, 테이블, 정규화 근거, Q&A 대비 | ✅ 초안 |
| [`docs/03_결정사항.md`](docs/03_결정사항.md) | 결정할 것과 결정된 것 | 🔶 의견 필요 |
| [`docs/04_API명세.md`](docs/04_API명세.md) | API 목록, JSON 응답 예시 | 🔶 목록만 |
| [`docs/05_실행가이드.md`](docs/05_실행가이드.md) | SQL 실행 방법과 기대 결과 | ✅ |
| [`sql/01_schema.sql`](sql/01_schema.sql) | CREATE TABLE | ✅ 실행 확인 |
| [`sql/02_sample_data.sql`](sql/02_sample_data.sql) | 스크린샷 기반 샘플 데이터 | ✅ 실행 확인 |
| [`sql/03_view_queries.sql`](sql/03_view_queries.sql) | 화면별 SELECT | ✅ 실행 확인 |
| `api/` | Flask API | ⬜ Phase 2 |

## 폴더 구조

```
term_project_melon/
├── README.md        ← 지금 이 문서
├── images/          ← 앱 스크린샷 (ERD 이미지도 여기에 추가 예정)
├── docs/            ← 계획, 분석, 설계, 결정사항, API 명세, 실행 가이드
├── sql/             ← 01 스키마 → 02 샘플 데이터 → 03 화면별 쿼리
└── api/             ← Flask API (Phase 2)
```
