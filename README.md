# payhere

## API
## **/signup**
- 회원가입 기능

    `request body` 형식
    ```json
    {
        "email": "string",
        "pw": "string"
    }
    ```
    위와 같은 형식으로 POST요청시 
    - 회원가입 완료 `{"isSuccess" : True, "message" : "SignUp success"}` 반환
    - 회원가입 실패 `{"isSuccess" : False, "message" : "실패이유" }` 반환

## **/signup**
- 로그인 기능

    `request body` 형식
    ```json
    {
        "email": "string",
        "pw": "string"
    }
    ```
    위와 같은 형식으로 POST요청시 
    - 로그인 완료 `{"isSuccess" : True ,"token" : "유저 토큰"}` 반환
    - 로그인 실패 `{"isSuccess" : False, "message" : "실패이유" }` 반환

## **/signout/{token}**
- 로그아웃 기능
    위와 같은 형식으로 DELETE요청시 
    - 로그아웃 완료 `{"isSuccess" : True ,"token" : "Sign Out success"}` 반환
    - 로그아웃 실패 `{"isSuccess" : False, "message" : "실패이유" }` 반환

## **/account/{token}**
- 가계부 등록 기능

    `request body` 형식
    ```json
    {
        "price": 0,
        "memo": "string",
        "date": "string"
    }
    ```
    위와 같은 형식으로 POST요청시 
    - 가계부 등록 완료 `{"isSuccess" : True, "message" : "Apply success"}` 반환
    - 가계부 등록 실패 `{"isSuccess" : False, "message" : "실패이유" }` 반환

## **/account/all/{token}**
- 가계부 리스트 검색 기능
    위와 같은 형식으로 GET요청시 
    - 가계부 리스트 검색 완료 반환 값
    ```
    {
        "2": {
            "memo": "pc방",
            "price": 1000,
            "date": "2023-04-10"
        },
        "3": {
            "memo": "점심 식사",
            "price": 7000,
            "date": "2023-04-10"
        },
        "4": {
            "memo": "제주 삼다수",
            "price": 1000,
            "date": "2023-04-10"
        }
    }
    ```
    - 가계부 리스트 검색 실패 `{"isSuccess" : False, "message" : "실패이유" }` 반환

## **/account/{accountID}/{token}**
- 가계부 세부 내역 검색 기능
    위와 같은 형식으로 GET요청시 
    - 가계부 세부 내역 검색 완료 반환 값
    ```
    {
        "date": "2023-04-10",
        "id": 3,
        "price": 7000,
        "update_at": "2023-04-10T17:32:56",
        "user_id": 1,
        "memo": "점심 식사",
        "register_at": "2023-04-10T17:32:56"
    }
    ```
    - 가계부 세부 내역 검색 실패 `{"isSuccess" : False, "message" : "실패이유" }` 반환

## **/account/{accountID}/table/{tableName}/value/{value}/{token}**
- 가계부 세부 내역 수정 기능
    위와 같은 형식으로 PUT요청시 
    - 가계부 세부 내역 수정 완료 `{"isSuccess" : True, "message" : "Update Success"}` 반환
    - 가계부 세부 내역 수정 실패 `{"isSuccess" : False, "message" : "실패이유" }` 반환

## **/account/{accountID}/{token}**
- 가계부 내역 삭제 기능
    위와 같은 형식으로 DELETE요청시 
    - 가계부 내역 삭제 완료 `{"isSuccess" : True, "message" : "delete success"}` 반환
    - 가계부 내역 삭제 실패 `{"isSuccess" : False, "message" : "실패이유" }` 반환

## **/account/copy/{accountID}/{token}**
- 가계부 내역 복제 기능
    위와 같은 형식으로 POST요청시
    - 가계부 내역 삭제 완료 `{"isSuccess" : True, "message" : "Copy success"}` 반환
    - 가계부 내역 삭제 실패 `{"isSuccess" : False, "message" : "실패이유" }` 반환

## **/account/make/link/{accountID}/{token}**
- 새부 내역 링크 공유 기능
    위와 같은 형식으로 GET요청시
    - 가계부 내역 삭제 완료 `{"isSuccess" : True, "url" : link}` 반환 -> 링크 규칙 URL+"/account/share/link/"+세부 내역을 JWT로 바꾼 코드
    - 가계부 내역 삭제 실패 `{"isSuccess" : False, "message" : "실패이유" }` 반환

## **/account/share/link/{token}**
- 새부 내역 링크 기능
    ```
    {
        "id": 3,
        "price": 7000,
        "memo": "점심 식사",
        "date": "2023-04-10",
        "create_at": "2023-04-10 17:32:56",
        "update_at": "2023-04-10 17:32:56"
    }
    ```