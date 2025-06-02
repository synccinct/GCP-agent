CLOUD_SQL_TEMPLATE = """
import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import datetime
from typing import Optional, List, Dict, Any
import os

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(50), default='user')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    projects = relationship("Project", back_populates="owner")
    tasks = relationship("Task", back_populates="assignee")

class Project(Base):
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    status = Column(String(50), default='active')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    owner = relationship("User", back_populates="projects")
    tasks = relationship("Task", back_populates="project")

class Task(Base):
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    assignee_id = Column(Integer, ForeignKey('users.id'))
    status = Column(String(50), default='pending')
    priority = Column(String(50), default='medium')
    due_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    project = relationship("Project", back_populates="tasks")
    assignee = relationship("User", back_populates="tasks")

class CloudSQLClient:
    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self) -> Session:
        return self.SessionLocal()
    
    def create_user(self, email: str, name: str, role: str = "user") -> User:
        with self.get_session() as session:
            user = User(email=email, name=name, role=role)
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
    
    def get_user(self, user_id: int) -> Optional[User]:
        with self.get_session() as session:
            return session.query(User).filter(User.id == user_id).first()
    
    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        with self.get_session() as session:
            return session.query(User).offset(skip).limit(limit).all()
    
    def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        with self.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                for key, value in kwargs.items():
                    setattr(user, key, value)
                user.updated_at = datetime.utcnow()
                session.commit()
                session.refresh(user)
            return user
    
    def delete_user(self, user_id: int) -> bool:
        with self.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                session.delete(user)
                session.commit()
                return True
            return False
"""

CLOUD_SQL_MIGRATIONS_TEMPLATE = """
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# Migration: Create users table
def upgrade_create_users():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('email', sa.String(255), unique=True, index=True, nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('role', sa.String(50), default='user'),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), default=datetime.utcnow)
    )

def downgrade_create_users():
    op.drop_table('users')

# Migration: Create projects table
def upgrade_create_projects():
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('owner_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('status', sa.String(50), default='active'),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), default=datetime.utcnow)
    )

def downgrade_create_projects():
    op.drop_table('projects')

# Migration: Create tasks table
def upgrade_create_tasks():
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('assignee_id', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('status', sa.String(50), default='pending'),
        sa.Column('priority', sa.String(50), default='medium'),
        sa.Column('due_date', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), default=datetime.utcnow)
    )

def downgrade_create_tasks():
    op.drop_table('tasks')
"""
