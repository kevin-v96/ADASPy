from fastapi import FastAPI
from adaspy.backend.auth import router as auth_router
from adaspy.backend.team import router as team_router
from adaspy.backend.agent import router as agent_router
from adaspy.backend.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()
@app.get("/")
def read_root():
    return {"Hello": "World"}

app.include_router(auth_router)
app.include_router(team_router)
app.include_router(agent_router)
