from contextlib import contextmanager
import os

from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.hybrid import hybrid_property


Base = declarative_base()


class FreecycleOffer(Base):
    __tablename__ = 'freecycle_offers'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=False)
    title = sa.Column(sa.String(255), nullable=False)
    notified = sa.Column(sa.Boolean, default=False)
    region = sa.Column(sa.String(255), nullable=False, primary_key=True)

    def __repr__(self):
        return f"<FreecycleOffer(id={self.id}, title={self.title}, notified={self.notified}, region={self.region})>"

    def __eq__(self, other):
        return self.id == other.id

    @property
    def url(self):
        return f"https://groups.freecycle.org/group/{self.region}/posts/{self.id}"


engine = sa.create_engine(os.environ.get("DATABASE_URL"))

Session = sessionmaker()
Session.configure(bind=engine)


@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        print(e)
        session.rollback()
    finally:
        session.close()
