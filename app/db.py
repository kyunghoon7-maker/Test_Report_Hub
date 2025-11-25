from sqlmodel import create_engine, Session, SQLModel

# 어떤 db 쓸지 결정
DATABASE_URL = "sqlite:///./reporthub.db"
# db 와 통신할 엔진 생성
engine = create_engine(DATABASE_URL, echo=True)

# 앱 시작 시 테이블을 만들어주는 초기화 함수
def init_db():
    from . import models  # 모델 등록용 import
    SQLModel.metadata.create_all(engine)

# 각 API 요청에서 사용할 DB 세션 제공 함수 
def get_session():
    with Session(engine) as session:
        yield session