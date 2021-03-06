from typing import List

from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from attendance.database import get_db
from attendance import schemas
from attendance.models import User
from attendance import crud
from attendance.dependency import get_current_user

router = APIRouter()

#LEAVE
#self
@router.get("/leave", status_code=200)
def leave_list(db: Session = Depends(get_db), current_user: User=Depends(get_current_user)):
    return crud.get_leaves(db, user_id=current_user.id)

@router.get("/leave/{id}", response_model= schemas.Leave, status_code=200)
def read_leave(id: int, db: Session=Depends(get_db), current_user: User=Depends(get_current_user)):
    return crud.get_leave(db, leave_id=id, current=current_user)

@router.post("/leave", status_code=201)
def add_leave(leave_form: schemas.LeaveCreate, db: Session=Depends(get_db), current_user: User=Depends(get_current_user)):
    return crud.create_leave(db, Leave=leave_form, user_id=current_user.id)

@router.put("/leave/{id}", status_code=200)
def update_leave(id:int, leave_from: schemas.LeaveCreate, db: Session=Depends(get_db), current_user: User=Depends(get_current_user)):
    return crud.update_leave(db, Leave=leave_from, current=current_user, id=id)

@router.delete("/leave/{id}", status_code=204)
def delete_leave(id: int, db: Session=Depends(get_db), current_user: User=Depends(get_current_user)):
    return crud.delete_leave(db, leave_id=id, current=current_user)

#manager
@router.get("/check_leave", status_code=200)
def check_leave_list(db: Session=Depends(get_db), current_user: User=Depends(get_current_user)):
    return crud.get_other_leaves(db, current=current_user)

@router.get("/check_leave/{id}", status_code=200)
def check_leave_read(id: int, db: Session=Depends(get_db), current_user: User=Depends(get_current_user)):
    return crud.get_leave_manager(db, current=current_user, id=id)

@router.put("/check_leave/{id}", response_model=schemas.Leave, status_code=200)
def check_leave(id: int, db: Session=Depends(get_db), current_user: User=Depends(get_current_user)):
    return crud.check_leave(db, id=id, current=current_user)