from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from adaspy.backend.models import AgenticSystem, User, Team, Membership
from adaspy.backend.database import get_db
from adaspy.backend.dependencies import get_current_user

router = APIRouter()


@router.post("/create_agent/")
def create_agent(name: str, description: str, code: str, metrics: dict,
                 team_id: int = None, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    if not current_user and not team_id:
        raise HTTPException(status_code=400, detail="Either the user must be logged in or a team ID must be provided")

    if team_id:
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

    new_agent = AgenticSystem(
        name=name,
        description=description,
        code=code,
        metrics=metrics,
        user_id=current_user.id if current_user else None,
        team_id=team_id
    )

    #add agent calling here

    db.add(new_agent)
    db.commit()
    return {"message": "Agentic system created successfully", "agent_id": new_agent.id}


@router.get("/get_agents/")
def get_agents(team_id: int = None, db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)):
    if not current_user and not team_id:
        raise HTTPException(status_code=400, detail="Either the user must be logged in or a team ID must be provided")
    membership = db.query(Membership).filter(Membership.user_id == current_user.id).first()

    if membership and membership.team_id == team_id:
        agents = db.query(AgenticSystem).filter(AgenticSystem.team_id == team_id).all()
    else:
        agents = db.query(AgenticSystem).filter(AgenticSystem.owner_id == current_user.id).all()
    return {"agents": agents}


@router.put("/update_agent/{agent_id}/")
def update_agent(agent_id: int, code: str = None, metrics: dict = None, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    agent = db.query(AgenticSystem).filter(AgenticSystem.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agentic system not found")
    membership = db.query(Membership).filter(Membership.user_id == current_user.id).first()
    if agent.team_id and membership and agent.team_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to update this agent")

    if code:
        agent.code = code
    if metrics:
        agent.metrics = metrics

    db.commit()
    return {"message": "Agentic system updated successfully"}


@router.delete("/delete_agent/{agent_id}/")
def delete_agent(agent_id: int, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    agent = db.query(AgenticSystem).filter(AgenticSystem.id == agent_id).first()

    if not agent:
        raise HTTPException(status_code=404, detail="Agentic system not found")

    if agent.team_id:
        membership = db.query(Membership).filter(Membership.user_id == current_user.id,
                                                 Membership.team_id == agent.team_id).first()
        if not membership:
            raise HTTPException(status_code=403, detail="You do not have permission to delete this agent")
    elif agent.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this agent")
    agent.is_deleted = True
    db.commit()

    return {"message": "Agentic system marked as deleted"}
