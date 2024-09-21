from fastapi import FastAPI
from .auth import router as auth_router
from .team import router as team_router
from .agent import router as agent_router
from .database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()
@app.get("/")
def read_root():
    return {"Hello": "World"}

app.include_router(auth_router)
app.include_router(team_router)
app.include_router(agent_router)
