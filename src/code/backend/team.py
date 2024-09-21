from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from .models import User, Team, Membership
from .database import get_db
from .dependencies import get_current_user  # Import the dependency to get the current user

router = APIRouter(prefix="/teams")


@router.post("/create_team/")
def create_team(name: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    existing_team = db.query(Team).filter(Team.name == name, Team.creator_id == current_user.id).first()
    if existing_team:
        raise HTTPException(status_code=400, detail="Team name already exists")

    new_team = Team(name=name,creator_id=current_user.id)
    db.add(new_team)
    db.commit()
    return {"message": "Team created successfully"}


@router.post("/invite_to_team/")
def invite_to_team(user_id: int, team_id: int, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id).first()
    team = db.query(Team).filter(Team.id == team_id).first()

    if not user or not team:
        raise HTTPException(status_code=404, detail="User or team not found")

    membership = db.query(Membership).filter(
        Membership.user_id == current_user.id,
        Membership.team_id == team_id
    ).first()

    if not membership:
        raise HTTPException(status_code=403, detail="You do not have permission to invite users to this team")
    existing_membership = db.query(Membership).filter(
        Membership.user_id == user_id,
        Membership.team_id == team_id
    ).first()

    if existing_membership:
        raise HTTPException(status_code=400, detail="User is already a member of the team")

    new_membership = Membership(user_id=user_id, team_id=team_id)
    db.add(new_membership)
    db.commit()
    return {"message": "User invited to team successfully"}


@router.post("/remove_from_team/")
def remove_from_team(user_id: int, team_id: int, db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    membership = db.query(Membership).filter(
        Membership.user_id == user_id,
        Membership.team_id == team_id
    ).first()

    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")
    current_membership = db.query(Membership).filter(
        Membership.user_id == current_user.id,
        Membership.team_id == team_id
    ).first()

    if not current_membership:
        raise HTTPException(status_code=403, detail="You do not have permission to remove users from this team")

    db.delete(membership)
    db.commit()
    return {"message": "User removed from team successfully"}
