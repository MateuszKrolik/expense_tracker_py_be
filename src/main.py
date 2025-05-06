import uvicorn
from fastapi import FastAPI

from routes.budget import router as budget_routes
from routes.category import router as category_routes
from routes.expense import router as expense_routes
from routes.auth import router as auth_routes
from routes.token import router as token_routes
from services.database import create_db_and_tables, seed_dummy_users

app = FastAPI()


app.include_router(token_routes)
app.include_router(auth_routes)
app.include_router(budget_routes)
app.include_router(category_routes)
app.include_router(expense_routes)


@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()
    for dummy_user in await seed_dummy_users():
        print(dummy_user.model_dump())


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
