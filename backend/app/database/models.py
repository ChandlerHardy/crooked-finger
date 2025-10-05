from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, date

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)

    # Relationships
    projects = relationship("CrochetProject", back_populates="user")
    chat_messages = relationship("ChatMessage", back_populates="user")
    conversations = relationship("Conversation", back_populates="user")

class CrochetProject(Base):
    __tablename__ = "crochet_projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    pattern_text = Column(Text)  # Original crochet pattern
    translated_text = Column(Text)  # AI-translated readable instructions
    difficulty_level = Column(String)  # beginner, intermediate, advanced
    estimated_time = Column(String)  # e.g., "2 hours"
    yarn_weight = Column(String)  # DK, Worsted, etc.
    hook_size = Column(String)  # 4mm, 5mm, etc.
    notes = Column(Text)  # User notes
    image_data = Column(Text)  # JSON array of base64 image strings
    is_completed = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="projects")
    chat_messages = relationship("ChatMessage", back_populates="project")
    diagrams = relationship("ProjectDiagram", back_populates="project")

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, default="New Chat")
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="conversations")
    chat_messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(Text)  # User's question/message
    response = Column(Text)  # AI's response
    message_type = Column(String, default="question")  # question, clarification, help
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True)
    project_id = Column(Integer, ForeignKey("crochet_projects.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="chat_messages")
    project = relationship("CrochetProject", back_populates="chat_messages")
    conversation = relationship("Conversation", back_populates="chat_messages")

class ProjectDiagram(Base):
    __tablename__ = "project_diagrams"

    id = Column(Integer, primary_key=True, index=True)
    diagram_data = Column(Text)  # SVG/JSON diagram data
    diagram_type = Column(String)  # stitch_diagram, pattern_chart, schematic
    diagram_format = Column(String, default="svg")  # svg, png, pdf
    project_id = Column(Integer, ForeignKey("crochet_projects.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    project = relationship("CrochetProject", back_populates="diagrams")

class AIModelUsage(Base):
    __tablename__ = "ai_model_usage"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String, index=True)  # gemini-2.5-pro, gemini-2.5-flash, etc.
    request_count = Column(Integer, default=0)
    total_input_characters = Column(Integer, default=0)  # Total input characters processed
    total_output_characters = Column(Integer, default=0)  # Total output characters generated
    total_input_tokens = Column(Integer, default=0)  # Estimated input tokens (chars / 4)
    total_output_tokens = Column(Integer, default=0)  # Estimated output tokens (chars / 4)
    date = Column(Date, default=date.today, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)