# 데이터베이스 텀프로젝트: 멜론 앱 DB 설계 & API

멜론 음악 앱의 화면 3개를 골라, 그 화면을 그리는 데 필요한 **데이터베이스를 설계**하고 **API를 개발**하는 팀 프로젝트입니다.

> 팀원은 이 README부터 읽고, 자세한 내용은 아래 문서 링크를 따라가 주세요.
> 정해지지 않은 사항은 [`docs/03_결정사항.md`](docs/03_결정사항.md)에 모아 두었습니다. 의견이 있으면 거기에 적어 주세요.

## 과제 요구사항 (TP_DB.pdf 요약)

- 모바일 앱 1개 + 화면 3개 이상 선택
- 화면을 만들기 위한 **DB 구축** + 각 화면의 **API 개발**
- **발표 (10분 + Q&A 5분)**: 앱/화면 소개 → DB 설계 → API
- **보고서**: 앱/화면 소개, DB 설계(테이블, 쿼리, 데이터셋, ERD), API(입력값, JSON 출력)
- 사용 도구 (Week9_2): **Python, VSCode, Postman, MySQL**

## 일정

| 날짜 | 내용 |
|---|---|
| **11/29 (일) 23:59** | 슬라이드 + 보고서 사이버캠퍼스 제출 |
| 12/1 (화) 또는 12/7 (월) | 발표 (우리 조 발표일에만 참석, 12/1은 오프라인) |
| 발표 후 | 동료 평가 (비공개 설문, 최종 점수에 반영) |

## 선택한 화면

| # | 화면 | 스크린샷 |
|---|---|---|
| 1 | 홈 (최신음악, 멜론차트) | [`images/view1_home.jpg`](images/view1_home.jpg) |
| 2 | 재생목록 | [`images/view2_play_queue.jpg`](images/view2_play_queue.jpg) |
| 3 | 음악서랍 > 좋아요 > 곡 | [`images/view3_like_songs.jpg`](images/view3_like_songs.jpg) |

<p>
  <img src="images/view1_home.jpg" width="220">
  <img src="images/view2_play_queue.jpg" width="220">
  <img src="images/view3_like_songs.jpg" width="220">
</p>

## 문서

| 문서 | 내용 | 상태 |
|---|---|---|
| [`docs/01_화면분석.md`](docs/01_화면분석.md) | 화면별로 필요한 데이터 정리 | 초안 완료 |
| [`docs/02_DB설계.md`](docs/02_DB설계.md) | 테이블 설계, 정규화 근거 | 초안 완료 (ERD, SQL은 아직) |
| [`docs/03_결정사항.md`](docs/03_결정사항.md) | 결정할 것 / 결정된 것 기록 | 진행 중 |
| `docs/04_API명세.md` | API 입력값, JSON 출력 | 아직 |

## 진행 상황

- [x] 과제 요구사항, 수업 자료(정규화, 설치 가이드) 정리
- [x] 화면 3개 선정 + 스크린샷
- [x] 화면별 필요 데이터 분석
- [x] 테이블 초안 + 정규화 포인트
- [ ] 결정사항 확정 ([`docs/03_결정사항.md`](docs/03_결정사항.md))
- [ ] ERD 그리기
- [ ] `sql/schema.sql` (CREATE TABLE)
- [ ] `sql/sample_data.sql` (스크린샷 속 곡으로 샘플 데이터)
- [ ] `sql/queries.sql` (화면별 SELECT 쿼리)
- [ ] API 개발 (Python) + Postman 테스트
- [ ] 보고서 작성
- [ ] 발표 슬라이드 작성

## 폴더 구조 (예정)

```
term_project_melon/
├── README.md          ← 지금 이 문서
├── images/            ← 앱 스크린샷
├── docs/              ← 분석, 설계, 결정사항, API 명세
├── sql/               ← schema, 샘플 데이터, 쿼리 (예정)
└── api/               ← Python API 서버 코드 (예정)
```
