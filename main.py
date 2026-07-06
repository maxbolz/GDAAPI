from datetime import datetime
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Session

from database import get_session
from models import GDArchive
from sqlmodel import SQLModel

app = FastAPI()


class GDArchiveRead(SQLModel):
    id: int
    level_name: str
    creator: str
    recorder: Optional[str]
    as_of: datetime
    link: List[str]
    upload_time_est: Optional[datetime]
    as_of: datetime


@app.get("/level/{level_id}", response_model=GDArchiveRead)
def get_level(level_id: int, session: Session = Depends(get_session)):
    level = session.get(GDArchive, level_id)
    if not (level and level.recorded and level.uploaded):
        raise HTTPException(status_code=404, detail="Level not found")
    return level