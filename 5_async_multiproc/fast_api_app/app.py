from fastapi import FastAPI

from config import API_TITLE, API_VERSION
from routes import items_router, misc_router

app = FastAPI(title=API_TITLE, version=API_VERSION)

app.include_router(misc_router)
app.include_router(items_router)


if __name__ == "__main__":
    import uvicorn
    from config import HOST, PORT
    uvicorn.run("app:app", host=HOST, port=PORT, reload=True)
