import uvicorn
from fastapi import FastAPI

from routes.budget import router as budget_routes
from routes.category import router as category_routes
from routes.expense import router as expense_routes
from services.database import create_db_and_tables

app = FastAPI()

app.include_router(budget_routes)
app.include_router(category_routes)
app.include_router(expense_routes)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
