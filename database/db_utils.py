from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from contextlib import contextmanager

engine = create_engine("sqlite:///emails.db", echo=True)
Base = declarative_base()


class Email(Base):
    """
    Represents an email record in the database with all relevant details.
    """
    __tablename__ = "emails"

    message_id = Column(String, primary_key=True)
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
        session.rollback()
        raise e
    finally:
        session.close()
