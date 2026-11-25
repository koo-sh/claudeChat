# HW6: Krible '내 관심사만 보기' API

`user_id`를 받아, 그 사용자가 하트(heart=1)한 **토픽** 또는 **종목**과 관련된 컨텐츠를
`update_time` 내림차순으로 돌려주는 API입니다.

## 실행
1. MySQL `krible` DB에 수업 자료(`Week11_2_DB_Workshop_krible_datasets.xlsx`)의 테이블과 데이터를 넣어 둡니다.
2. `main.py`의 `DB_CONFIG`에서 비밀번호를 본인 것으로 바꿉니다.
3. 실행
   ```
   pip install fastapi uvicorn pymysql
   uvicorn main:app --reload
   ```
4. 브라우저에서 `http://127.0.0.1:8000/latest/my-interest?user_id=1` (1~5)를 열거나,
   `http://127.0.0.1:8000/docs`에서 **Try it out**으로 실행합니다.

## 예상 결과 (content_id, 최신순)
| user_id | 개수 | content_id |
|---|---|---|
| 1 | 9 | 10, 9, 8, 6, 4, 3, 1, 11, 12 |
| 2 | 3 | 10, 6, 11 |
| 3 | 4 | 10, 4, 1, 11 |
| 4 | 2 | 7, 2 |
| 5 | 3 | 3, 11, 12 |
