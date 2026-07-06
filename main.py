from datetime import datetime, timezone
from typing import List, Optional
from zoneinfo import ZoneInfo

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
    link: List[str]
    upload_time_est: Optional[datetime]
    as_of: datetime


@app.get("/level/{level_id}", response_model=GDArchiveRead)
def get_level(level_id: int, session: Session = Depends(get_session)):
    level = session.get(GDArchive, level_id)

    if level is None:
        raise HTTPException(status_code=404, detail="Level not found")
    if not (level.recorded and level.uploaded):
        raise HTTPException(status_code=404, detail="Level not found")

    est = ZoneInfo("America/New_York")
    est_now = datetime.now(est)
    upload_time = level.upload_time_est.replace(tzinfo=est)
    
    if upload_time is None or upload_time > est_now:
        raise HTTPException(status_code=404, detail="Level not found")
    
    return level