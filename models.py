from datetime import datetime
from typing import List, Optional

from sqlalchemy import ARRAY, Column, String
from sqlmodel import DateTime, Field, SQLModel


class GDArchive(SQLModel, table=True):
    __tablename__ = "gd_archives"

    id: int = Field(sa_column=Column("ID", primary_key=True))

    level_name: str = Field(sa_column=Column("Level Name", nullable=False))
    creator: str = Field(sa_column=Column("Creator", nullable=False))
    recorder: Optional[str] = Field(default=None, sa_column=Column("Recorder"))
    as_of: datetime = Field(default_factory=datetime.now, sa_column=Column("as_of", DateTime, nullable=False))
    song: Optional[str] = Field(default=None, sa_column=Column("Song"))
    song_id: Optional[int] = Field(default=None, sa_column=Column("Song ID"))
    length: Optional[str] = Field(default=None, sa_column=Column("Length"))
    difficulty: Optional[str] = Field(default=None, sa_column=Column("Difficulty"))
    reward: Optional[int] = Field(default=None, sa_column=Column("Reward"))
    rate: bool = Field(default=False, sa_column=Column("Rate"))
    coins: Optional[int] = Field(default=None, sa_column=Column("Coins"))
    notable_info: Optional[str] = Field(default=None, sa_column=Column("Notable Info"))
    recorded: bool = Field(default=False, sa_column=Column("Recorded?"))
    uploaded: bool = Field(default=False, sa_column=Column("Uploaded?"))
    thumbnail: bool = Field(default=False, sa_column=Column("Thumbnail?"))
    link: List[str] = Field(default_factory=list, sa_column=Column("Link", ARRAY(String)))
    upload_time_est: Optional[datetime] = Field(default=None, sa_column=Column("Upload Time (EST)"))
    as_of: datetime = Field(default_factory=datetime.now, sa_column=Column("As Of", DateTime, nullable=False))