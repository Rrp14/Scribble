from fastapi import FastAPI
import uvicorn
from contextlib import asynccontextmanager
from src.data.database import connect_to_mongo,close_mongo
from src.web.note import router as note_router
from src.auth.routes.auth import router as auth_router
from src.core.exceptions import value_error_handler


@asynccontextmanager
async def lifespan(app:FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo()


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(note_router)

app.add_exception_handler(ValueError,value_error_handler)

@app.get("/")
async def root():
    return {"message": "Notes API running"}









if __name__=="__main__":
    uvicorn.run("main:app",reload=True,port=9000)

