from fastapi import FastAPI
from routers import auth, posts

app = FastAPI()

app.include_router(auth.auth_router)
app.include_router(posts.post_router)

