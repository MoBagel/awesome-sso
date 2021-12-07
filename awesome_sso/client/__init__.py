from fastapi import FastAPI

from awesome_sso.client.route import router


class Client:

    @staticmethod
    def init_app(app: FastAPI):
        app.include_router(router)
