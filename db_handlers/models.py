from sqlalchemy import (TIME, BigInteger, Boolean, Column, ForeignKey, Integer,
                        String, func)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    user_id = Column(BigInteger, primary_key=True, autoincrement=False)
    username = Column(String, nullable=False)
    job_name = Column(String, nullable=True)
    schedule_time = Column(TIME)
    schedule_on = Column(Boolean, default=False)

    jobs = relationship('Job', back_populates='user')


class Job(Base):
    __tablename__ = 'job'

    id = Column(BigInteger, primary_key=True, autoincrement=False)
    title = Column(String, nullable=False)
    job_from = Column(String)
    salary = Column(String)
    company = Column(String)
    user_id = Column(BigInteger, ForeignKey('user.user_id'))
    link = Column(String)

    user = relationship('User', back_populates='jobs')