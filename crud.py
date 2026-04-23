from schemas import NoteCreate, NoteResponse
from database import db_dependency
from models import Note
from datetime import datetime


def create_note(db: db_dependency, note: NoteCreate, user_id: int):
    db_note = Note(
        title=note.title,
        body=note.body,
        tags=",".join(note.tags),
        pinned=note.pinned,
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat(),
        user_id=user_id
    )

    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    db_note.tags = db_note.tags.split(",") if db_note.tags else []
    return db_note

def get_all_notes(db: db_dependency, user_id: int):
    notes = db.query(Note).filter(Note.user_id == user_id).all()
    for note in notes:
        note.tags = note.tags.split(",") if note.tags else []
    return notes

def delete_note(db:db_dependency, note_id: int, user_id : int):
    note = db.query(Note).filter(Note.id == note_id, Note.User_id == user_id).first()
    if not note:
        return None
    db.delete(note)
    db.commit()
    return {"message": "Note deleted successfully"}
    
    
