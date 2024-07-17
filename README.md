
# `FASTAPI JWT AUTH SAMPLE`

FastAPI based jwt authorization microservice sample.
___

## *Project Status*

***Completed v0.0.1 &#10003;***

___
## Functionality
#### Users API
/user
```
- [GET] /api/v1/user: list all users.
- [GET] /api/v1/user/{user_id}: get specific user by id.
- [POST] /api/v1/user: add user.
- [PATCH] /api/v1/user/{user_id}: update existing user by id.
- [DELETE] /api/v1/user/{user_id}: delete existing user by id.
```

/auth
```
- [POST] /api/v1/auth/token: login for access & refresh token.
- [POST] /api/v1/auth/refresh: refresh access token with cookie-stored refresh one.
- [POST] /api/v1/auth/logout: remove existing refresh token from db and cookies.
```

## Technologies and Frameworks
- [Python 3.11.6](https://www.python.org/downloads/release/python-3116/)
- [FastAPI 0.108](https://fastapi.tiangolo.com/)
- [Uvicorn 0.25.0](https://www.uvicorn.org/settings/)
- [SQLAlchemy 2.0.31](https://docs.sqlalchemy.org/en/20/)
- [Alembic 1.13.1](https://alembic.sqlalchemy.org/en/latest/)
- [Pydantic 2.7.4](https://docs.pydantic.dev/latest/)
- PostgreSQL 16
- Docker 26.1.3
- Docker Compose 2.27.0
- [Pytest 8.1.1](https://doc.pytest.org/en/latest/announce/release-8.1.1.html)
- CI
___

## Development

1. Clone the repository to the local machine

    ```shell
    git clone https://github.com/Segfaul/fastapi_jwt_sample.git
    сd fastapi_jwt_sample/
    ```

2. Build images and run app in dev mode

    ```shell
    docker compose -f docker-compose.dev.yml up -d --build
    ```

3. Checkout http://127.0.0.1:8000/api/swagger (Uvicorn, Swagger)
    
    ```shell
    # Also you may run tests if needed
    docker exec -it users_app_dev-users_api-1 bash
    pytest backend/users/
    exit
    ```

4. Stop/Down the app

    ```shell
    # Without removing containers
    docker compose -f docker-compose.dev.yml stop

    # Removing containers
    docker compose -f docker-compose.dev.yml down

    # Removing containers and docker volumes (not local ones)
    docker compose -f docker-compose.dev.yml down -v
    ```
___