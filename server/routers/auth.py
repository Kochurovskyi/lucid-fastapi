from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, EmailStr
from models import Users
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import SessionLocal
from typing import Annotated
from fastapi import Depends
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone


auth_router = APIRouter(prefix='/auth', tags=['auth'])
SECRET_KEY = 'd13df32'
ALGORYTHM = 'HS256'
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oath2_bearer = OAuth2PasswordBearer(tokenUrl='auth/login')


def login_user(email: str, password: str, db: Session):
    """Check if the user exists and the password is correct."""
    user = db.query(Users).filter(Users.email == email).first()
    if user is None: return False
    if not bcrypt_context.verify(password, user.password): return False
    return user

def create_access_token(email: str, user_id: int, expires_in: timedelta):
    """Create the access token."""
    payload = {'sub': email, 'id': user_id}
    expires_in = datetime.now(timezone.utc) + expires_in
    payload.update({'exp': expires_in})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORYTHM)

async def get_current_user(token: str = Depends(oath2_bearer)):
    """Get the current user after token verification."""
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORYTHM])
        email: str = payload.get('sub')
        user_id: int = payload.get('id')
        if email is None or user_id is None: raise credentials_exception
        return {'email': email, 'id': user_id}
    except JWTError: raise credentials_exception


def get_db():
    """Get the database session and close it after the request is done."""
    db = SessionLocal()
    try: yield db
    finally: db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_form_data = Annotated[OAuth2PasswordRequestForm, Depends(OAuth2PasswordRequestForm)]


class CreateUserRequest(BaseModel):
    """Request model for the user endpoint."""
    email: str = EmailStr
    password: str = Field(min_length=4, max_length=10)


class Token (BaseModel):
    """Model for the token response."""
    access_token: str
    token_type: str


@auth_router.post('/signup', status_code=status.HTTP_201_CREATED,
                  responses={201: {"description": "User created"}})
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    """Create a new user."""
    existing_user = db.query(Users).filter(Users.email == create_user_request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    create_user_data = Users(email=create_user_request.email,
                             password=bcrypt_context.hash(create_user_request.password))
    db.add(create_user_data)
    db.commit()
    return {"message": "User created successfully"}


@auth_router.post('/login', response_model=Token, responses={
    200: {"description": "Successful login", "content": {"application/json": {"example": {"access_token": "string", "token_type": "bearer"}}}},
    401: {"description": "Invalid credentials"},
    503: {"description": "Service unavailable - something went wrong with token"}})
async def login_for_access_token(form_data: user_form_data, db: db_dependency):
    """Login and get the access token."""
    user = login_user(form_data.username, form_data.password, db)
    if not user: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    try:
        token = create_access_token(form_data.username, user.id, timedelta(minutes=5))
        return {'access_token': token, 'token_type': 'bearer'}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=503, detail="Service unavailable - something went wrong with token")