from typing import Union 
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def start():
    return {"message": "hello_world!"}

