from fastapi.testclient import TestClient
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends
from sqlalchemy.orm import Session

from attendance.main import app, login
from attendance import crud
from attendance.database import get_db
import json

client = TestClient(app)

async def override_dependency(form_data: OAuth2PasswordRequestForm= Depends(), db:Session=Depends(get_db)):
    user_dict = crud.authenticate_user(db, account=form_data.username, passwd=form_data.password)
    return {"access_token": user_dict.account, "token_type": "bearer"}

app.dependency_overrides[login] = override_dependency

officer = {"accept": "application/json", "Authorization": "Bearer officer1", "Content-Type": "application/json"}
admin = {"accept": "application/json", "Authorization": "Bearer admin", "Content-Type": "application/json"}

def test_create_daily_admin():
    daily = {
        'on_fix': '08:00',
        'off_fix': '17:00',
        'fix_note': '他會成功',
    }
    daily_json = json.dumps(daily)
    response = client.put("/hr/daily/{1}", data=daily_json, headers=admin)
    assert response.status_code == 201
    print(response.json())