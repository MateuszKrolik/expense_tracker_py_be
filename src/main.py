import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.private.user import router as user_routes
from routes.public.token import router as token_routes
from routes.public.auth import router as auth_routes
from routes.public.expense import router as public_expense_router
from services.database import create_db_and_tables, seed_dummy_users
import tracemalloc

tracemalloc.start()  # detailed logs of not awaited coroutines

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Change to .ENV once deployed
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_routes)
app.include_router(token_routes)
app.include_router(auth_routes)
app.include_router(public_expense_router)


@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()
    for dummy_user in await seed_dummy_users():
        print(dummy_user.model_dump())


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
