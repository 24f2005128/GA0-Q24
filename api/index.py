from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import csv

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


def load_students():
    with open("q-fastapi.csv", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


@app.get("/")
async def get_students(
    class_: list[str] | None = Query(default=None, alias="class")
):
    students = load_students()

    if class_:
        students = [
            student
            for student in students
            if student["class"] in class_
        ]

    return {"students": students}
