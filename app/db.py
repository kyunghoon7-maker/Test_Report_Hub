from sqlmodel import create_engine, Session, SQLModel

DATABASE_URL = "sqlite:///./reporthub.db"
engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    from . import models  # 모델 등록용 import
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session