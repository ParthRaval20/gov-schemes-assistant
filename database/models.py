from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Scheme(Base):

    __tablename__ = "schemes"

    id = Column(Integer, primary_key=True, index=True)

    scheme_name = Column(String)
    description = Column(Text)
    benefits = Column(Text)
    eligibility = Column(Text)
    documents_required = Column(Text)

    application_link = Column(String)
    state = Column(String)
    category = Column(String)
    