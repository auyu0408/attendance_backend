from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import mode
from attendance import models, schemas
from passlib.context import CryptContext
from fastapi import HTTPException
import datetime 

#hash passwd
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def authenticate_user(db:Session, account: str, passwd:str):
    user = db.query(models.User).filter(models.User.account == account, models.User.status==0).first()
    if not user:
        raise HTTPException(status_code=404, detail="Incorrect user account")
    if pwd_context.verify(passwd, user.passwd):
        return user
    else:
        raise HTTPException(status_code=400, detail="Wrong password.")  

def get_user_account(db:Session, user_account: str):
    db_user = db.query(models.User).filter(models.User.account==user_account, models.User.status==0).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Can't find User or User is resigned.",
            headers={"WWW-Authenticate": "Bearer"},)
    return db_user

def update_passwd(db:Session, passwd: schemas.UserPasswd, user_id: int):
    db_user = db.query(models.User).filter(models.User.id==user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if pwd_context.verify(passwd.origin, db_user.passwd):
        hash_new = pwd_context.hash(passwd.new)
        db_user.passwd = hash_new
        db.commit()
        return True
    else:
        raise HTTPException(status_code=400, detail="Wrong password.")

#hr
def get_users(db: Session, current: models.User, skip: int=0, limit: int=100):
    if not current.hr:
        raise HTTPException(status_code=401, detail="You are not hr.")
    return db.query(models.User).offset(skip).limit(limit).all()

def get_user(db:Session, user_id: int, current: models.User):
    if not current.hr:
        raise HTTPException(status_code=401, detail="You are not a hr.")
    db_user = db.query(models.User).filter(models.User.id==user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")
    return db_user

def create_user(db:Session, user:schemas.UserCreate, current: models.User):
    if not current.hr:
        raise HTTPException(status_code=401, detail="Your are not hr.")
    hash_passwd = pwd_context.hash(user.passwd)
    account = db.query(models.User).filter(models.User.account == user.account).first()
    email = db.query(models.User).filter(models.User.email == user.email).first()
    if account:
        raise HTTPException(status_code=400, detail="Account is conflict.")
    if email:
        raise HTTPException(status_code=400, detail="Email is conflict.")
    db_user = models.User(name=user.name, account=user.account, email=user.email, passwd=hash_passwd,
            department = user.department, manager = user.manager, hr = user.hr, on_job = user.on_job, off_job=user.off_job
            , status=0)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db:Session, user_id: int, current: models.User):
    if not current.hr:
        raise HTTPException(status_code=401, detail="Your are not hr.")
    db_user = db.query(models.User).filter(models.User.id==user_id, models.User.status!=2).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")
    db_user.status= 2
    db_user.off_job= datetime.date.today()
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db:Session, user: schemas.UserUpdate, current: models.User, id: int):
    if not current.hr:
        raise HTTPException(status_code=401, detail="Your are not hr.")
    account = db.query(models.User).filter(models.User.id != id, models.User.account == user.account).first()
    email = db.query(models.User).filter(models.User.id != id, models.User.email == user.email).first()
    if account:
        raise HTTPException(status_code=400, detail="Account is conflict.")
    if email:
        raise HTTPException(status_code=400, detail="Email is conflict.")
    db_user = db.query(models.User).filter(models.User.id == id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")
    if db_user.status == 2:
        raise HTTPException(status_code=403, detail="User is resigned, the file can't edit.")
    if user.status == 2:
        raise HTTPException(status_code=403, detail="Wrong request way.")
    db_user.name= user.name
    db_user.account= user.account
    db_user.email= user.email
    db_user.department= user.department
    db_user.manager= user.manager
    db_user.hr= user.hr
    db_user.on_job= user.on_job
    db_user.status= user.status
    db.commit()
    db.refresh(db_user)
    return db_user