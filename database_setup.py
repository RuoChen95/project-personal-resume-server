from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class PersonName(Base):
    __tablename__ = 'person_name'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)


class ResumeItem(Base):
    __tablename__ = 'resume_item'
    
    type = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    content = Column(String(2500))
    restaurant_id = Column(Integer, ForeignKey('person_name.id'))
    restaurant = relationship(PersonName, cascade="all")
    
    # We added this serialize function to be able to send JSON objects in a serializable format
    @property
    def serialize(self):
        return {
            'type': self.type,
            'content': self.content,
            'id': self.id,
        }


engine = create_engine('sqlite:///personalResume.db')

Base.metadata.create_all(engine)