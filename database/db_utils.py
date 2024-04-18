from sqlalchemy import Column, Integer, String, Text, DATETIME, Boolean, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from contextlib import contextmanager

engine = create_engine("sqlite:///emails.db", echo=True)
Base = declarative_base()

class Email(Base):
    __tablename__ = "emails"

    id = Column(String, primary_key=True)
    from_email = Column(String)
    subject = Column(String)
    date_received = Column(Integer)

Base.metadata.create_all(engine)

session_local = sessionmaker(bind=engine)

@contextmanager
def get_db_session():
    session = session_local()
    try:
        yield session
    except Exception as e:
        session.rollback()  # Rollback on errors
        raise e  # Re-raise to propagate errors
    finally:
        session.close()