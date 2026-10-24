from fastapi import APIRouter

router = APIRouter(tags=["misc"])


@router.get("/")
def root():
    return {"message": "Hello, FastAPI is running!"}


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/echo")
def echo(text: str, times: int = 1):
    return {"echo": " ".join([text] * times)}
