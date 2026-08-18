USERS_DB = {
    "student01": {"password": "pass123", "role": "user"},
    "student02": {"password": "pass123", "role": "user"},
    "admin01": {"password": "admin123", "role": "admin"},
}

EXAMS_DB: dict[int, dict] = {
    1: {"id": 1, "name": "Kỳ thi Toán học kỳ 1", "locked": False},
    2: {"id": 2, "name": "Kỳ thi Anh văn học kỳ 1", "locked": False},
}

RESULTS_DB: dict[str, list[dict]] = {
    "student01": [{"exam_id": 1, "score": 8.5}],
    "student02": [{"exam_id": 1, "score": 7.0}],
}

_next_exam_id = 3


def create_exam(name: str) -> dict:
    global _next_exam_id
    exam = {"id": _next_exam_id, "name": name, "locked": False}
    EXAMS_DB[_next_exam_id] = exam
    _next_exam_id += 1
    return exam


def lock_exam(exam_id: int) -> dict | None:
    exam = EXAMS_DB.get(exam_id)
    if exam is not None:
        exam["locked"] = True
    return exam


def delete_exam(exam_id: int) -> bool:
    return EXAMS_DB.pop(exam_id, None) is not None
