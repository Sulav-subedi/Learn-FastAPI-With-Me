from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine, db_dependency
from models import User, Note
from schemas import NoteBase, NoteResponse, NoteCreate, UserCreate, Token, UserInfo
import crud
from typing import List
from datetime import datetime
import auth
from fastapi.security import OAuth2PasswordRequestForm
from auth import get_current_user


Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
def read_root():
    return {"Message": "You are at the root"}

@app.post("/notes", response_model = NoteResponse)
def create_note_endpoint(note: NoteBase, db: db_dependency, current_user: User = Depends(get_current_user)):
    return crud.create_note(db, note, current_user.id)

@app.get("/notes", response_model=List[NoteResponse])
def get_all_notes_endpoint(db: db_dependency, current_user: User = Depends(get_current_user)):
    return crud.get_all_notes(db, current_user.id)

@app.put("/notes/{note_id}", response_model = NoteResponse)
def update_note(note_id: int, updated_note : NoteCreate, db: db_dependency):
    db_note = db.query(Note).filter(Note.id == note_id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    db_note.title = updated_note.title
    db_note.body = updated_note.body
    db_note.tags = ",".join(updated_note.tags)
    db_note.pinned = updated_note.pinned
    db_note.updated_at=datetime.now().isoformat()
    db.commit()
    db.refresh(db_note)
    
    return{
        "id": db_note.id,
        "title": db_note.title,
        "body": db_note.body,
        "tags": db_note.tags.split(",") if db_note.tags else [],
        "pinned": db_note.pinned,
        "created_at": db_note.created_at,
        "updated_at": db_note.updated_at
    }

@app.delete("/notes/{note_id}")
def delete_note(note_id: int, db: db_dependency, current_user: User = Depends(get_current_user)):
    return crud.delete_note(db, note_id, current_user.id)


@app.post("/users/signup")
def signup(user: UserCreate, db: db_dependency):

    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed = auth.hash_password(user.password)

    db_user = User(username=user.username, password = hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {"message": "User created successfully"}

@app.post("/login", response_model=Token)
def login( db: db_dependency, form_data : OAuth2PasswordRequestForm = Depends()):

    db_user = db.query(User).filter(User.username == form_data.username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not auth.verify_password(form_data.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid password")

    access_token = auth.create_access_token(data={"sub": db_user.username})
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

