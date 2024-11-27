from sqlalchemy import Column, Integer, String, BigInteger, TIMESTAMP, DATE, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    user_id = Column(BigInteger, primary_key=True, autoincrement=False)
    username = Column(String, nullable=False)
    job_name = Column(String)
    
    jobs = relationship('Job', back_populates='user')


class Job(Base):
    __tablename__ = 'job'

    id = Column(BigInteger, primary_key=True, autoincrement=False)
    title = Column(String, nullable=False)
    job_from = Column(String)
    location = Column(String)
    user_id = Column(BigInteger, ForeignKey('user.user_id'))
    link = Column(String)

    user = relationship('User', back_populates='jobs')