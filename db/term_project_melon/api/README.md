# api/ : Flask API 실행 방법

## 1. 준비
```bash
cd api
python -m venv .venv
.venv\Scripts\activate          # Windows   (mac: source .venv/bin/activate)
pip install -r requirements.txt
copy config.example.py config.py   # mac: cp config.example.py config.py
```
`config.py` 를 열어 `DB_PASSWORD` 에 자기 PC 의 MySQL root 비밀번호를 적어요.
(`config.py` 는 카톡·ZIP 으로 올리지 않아요.)

## 2. DB 준비
MySQL Workbench 에서 `sql/01_schema.sql` → `sql/02_sample_data.sql` 순서로 실행 (docs/05_실행가이드.md)

## 3. 서버 실행
```bash
python app.py
```
→ `http://localhost:5000` 에서 대기. 브라우저에서 `http://localhost:5000/api/home/chart` 를 열면 JSON 이 보여요.

## 4. Postman 테스트
`postman_collection.json` 을 Postman 에서 **Import** 하면 API 11개가 폴더별로 들어와요.
응답 예시는 `docs/04_API명세.md` 에 있어요.

## 5. 파일 설명
| 파일 | 내용 |
|---|---|
| `app.py` | API 11개 (라우트 + SQL). `sql/03_view_queries.sql` 의 쿼리를 그대로 사용 |
| `db.py` | pymysql 연결, `fetch_all / fetch_one / transaction()` |
| `config.example.py` | DB 접속 설정 틀. 복사해서 `config.py` 로 |
| `requirements.txt` | flask, pymysql |
| `postman_collection.json` | Postman 요청 모음 |

## 6. 테스트용 `now` 파라미터
멜론차트와 "잊고 지낸" 은 "지금 시각" 을 기준으로 계산해요. 샘플 데이터(2026-11-15) 기준으로 결과를 고정해서 보고 싶으면
`?now=2026-11-15 23:30:00` 을 붙이면 돼요. 생략하면 MySQL 의 `NOW()` 를 써요.
