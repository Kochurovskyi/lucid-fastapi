from fastapi import APIRouter
from fastapi import FastAPI, Depends, HTTPException, Path
from typing import Annotated
from models import Posts
from sqlalchemy.orm import Session
from database import SessionLocal
from starlette import status
from pydantic import BaseModel, Field
from fastapi import Request
from .auth import get_current_user
from aiocache import cached
from aiocache.serializers import JsonSerializer

post_router = APIRouter(prefix='/posts', tags=['posts'])

def get_db():
    """Get the database session and close it after the request is done."""
    db = SessionLocal()
    try: yield db
    finally: db.close()

async def validate_payload_size(request: Request):
    """Validate the size of the payload. If the payload is larger than 1 MB, return a 400 error."""
    max_payload_size = 1024 * 1024 # 1 MB
    if request.headers.get('content-length') and int(request.headers.get('content-length')) > max_payload_size:
        raise HTTPException(status_code=400, detail="Bad request - payload oversize")
    return await request.body()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class PostRequest(BaseModel):
    """Request model for the post endpoint."""
    title: str = Field(min_length=5, max_length=50)
    description: str = Field(min_length=10, max_length=1000)
    tag: str = Field(min_length=3, max_length=20)


@cached(ttl=300, key_builder=lambda f, *args, **kwargs: f"{kwargs['user']['id']}_posts", serializer=JsonSerializer())
@post_router.get('/', status_code=status.HTTP_200_OK,
                 responses={200: {"description": "Posts retrieved successfully"},
                            401: {"description": "Authentication failed"}})
async def read_all(user: user_dependency, db: db_dependency):
    """Get all the posts from the DB only for relevant logged user."""
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    posts = db.query(Posts).filter(Posts.owner_id == user.get('id')).all()
    return posts


@post_router.get('/post/{post_id}',
         status_code=status.HTTP_200_OK,
         responses={200: {"description": "Post found"},
                    404: {"description": "Post not found"},
                    401: {"description": "Authentication failed"}})
async def read_post(user: user_dependency, db: db_dependency, post_id: int = Path(gt=0)):
    """Get a post by its ID."""
    if user is None: raise HTTPException(status_code=401, detail="Authentication failed")
    data_requested = db.query(Posts).filter(Posts.id == post_id).filter(Posts.owner_id == user.get('id')).first()
    if data_requested is not None: return data_requested
    raise HTTPException(status_code=404, detail="Post not found")


@post_router.post('/post',
                  status_code=status.HTTP_201_CREATED,
                  responses={201: {"description": "Post created"},
                             400: {"description": "Bad request - payload oversize"},
                             401: {"description": "Authentication failed"}})
async def create_post(user: user_dependency, db: db_dependency, request: Request, post: PostRequest, payload: bytes = Depends(validate_payload_size)):
    """Create a new post. Validate the payload size (Not More than 1MB)."""
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    new_post = Posts(title=post.title, description=post.description, tag=post.tag, owner_id=user.get('id'))
    db.add(new_post)
    db.commit()
    return {"message": "Post created successfully"}


@post_router.put('/post/{post_id}',
                 status_code=status.HTTP_204_NO_CONTENT,
                 responses={204: {"description": "Post updated"},
                            401: {"description": "Authentication failed"},
                            404: {"description": "Post not found"},
                            400: {"description": "Bad request"}})
async def update_post(user: user_dependency, post: PostRequest, db: db_dependency,
                      post_id: int = Path(gt=0),
                      payload: bytes = Depends(validate_payload_size)):
    """Update a post by its ID. Validate the payload size (Not More than 1MB)."""
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    data_requested = db.query(Posts).filter(Posts.id == post_id).filter(Posts.owner_id == user.get('id')).first()
    if data_requested is None:
        raise HTTPException(status_code=404, detail="Post not found")
    data_requested.title = post.title
    data_requested.description = post.description
    data_requested.tag = post.tag
    db.commit()
    return {"message": "Post updated successfully"}


@post_router.delete('/post/{post_id}',
            status_code=status.HTTP_204_NO_CONTENT,
            responses= {204: {"description": "Post deleted"},
                        401: {"description": "Authentication failed"},
                        404: {"description": "Post not found"}})
async def delete_post(user: user_dependency, db: db_dependency, post_id: int = Path(gt=0)):
    """Delete a post by its ID."""
    if user is None: raise HTTPException(status_code=401, detail="Authentication failed")
    data_requested = db.query(Posts).filter(Posts.id == post_id).filter(Posts.owner_id == user.get('id')).first()
    if data_requested is None: raise HTTPException(status_code=404, detail="Post not found")
    db.delete(data_requested)
    db.commit()
    return {"message": "Post deleted successfully"}
