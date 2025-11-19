from sqlalchemy import Column, Text, Integer, LargeBinary, Index
from sqlalchemy.dialects.postgresql import JSONB
from src.database.base_model import Base

class CheckpointBlob(Base):
    __tablename__ = "checkpoint_blobs"
    
    thread_id = Column(Text, primary_key=True, nullable=False)
    checkpoint_ns = Column(Text, primary_key=True, nullable=False, default='')
    channel = Column(Text, primary_key=True, nullable=False)
    version = Column(Text, primary_key=True, nullable=False)
    type = Column(Text, nullable=False)
    blob = Column(LargeBinary, nullable=True)
    
    __table_args__ = (
        Index('checkpoint_blobs_thread_id_idx', 'thread_id'),
    )
    
    def __repr__(self):
        return f"<CheckpointBlob(thread_id='{self.thread_id}', checkpoint_ns='{self.checkpoint_ns}', channel='{self.channel}', version='{self.version}')>"


class CheckpointMigrations(Base):
    __tablename__ = "checkpoint_migrations"
    
    v = Column(Integer, primary_key=True, nullable=False)
    
    def __repr__(self):
        return f"<CheckpointMigrations(v={self.v})>"


class CheckpointWrites(Base):
    __tablename__ = "checkpoint_writes"
    
    thread_id = Column(Text, primary_key=True, nullable=False)
    checkpoint_ns = Column(Text, primary_key=True, nullable=False, default='')
    checkpoint_id = Column(Text, primary_key=True, nullable=False)
    task_id = Column(Text, primary_key=True, nullable=False)
    idx = Column(Integer, primary_key=True, nullable=False)
    channel = Column(Text, nullable=False)
    type = Column(Text, nullable=True)
    blob = Column(LargeBinary, nullable=True)
    task_path = Column(Text, nullable=False, default='')
    
    __table_args__ = (
        Index('checkpoint_writes_thread_id_idx', 'thread_id'),
    )
    
    def __repr__(self):
        return f"<CheckpointWrites(thread_id='{self.thread_id}', checkpoint_ns='{self.checkpoint_ns}', checkpoint_id='{self.checkpoint_id}', task_id='{self.task_id}', idx={self.idx})>"


class Checkpoints(Base):
    __tablename__ = "checkpoints"
    
    thread_id = Column(Text, primary_key=True, nullable=False)
    checkpoint_ns = Column(Text, primary_key=True, nullable=False, default='')
    checkpoint_id = Column(Text, primary_key=True, nullable=False)
    parent_checkpoint_id = Column(Text, nullable=True)
    type = Column(Text, nullable=True)
    checkpoint = Column(JSONB, nullable=False)
    metadata_ = Column("metadata", JSONB, nullable=False, default={})  # 👈

    __table_args__ = (
        Index('checkpoints_thread_id_idx', 'thread_id'),
    )

    def __repr__(self):
        return (
            f"<Checkpoints(thread_id='{self.thread_id}', "
            f"checkpoint_ns='{self.checkpoint_ns}', "
            f"checkpoint_id='{self.checkpoint_id}')>"
        )


