from sqlalchemy import Column, Integer, String, Date, Text, Boolean, JSON
from database import Base

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    formation = Column(String(50), nullable=False)
    priorite_retour = Column(String(20), nullable=False)
    type_retour = Column(String(50), nullable=False)
    date = Column(Date, nullable=False)
    rating = Column(Integer, nullable=False)
    comments = Column(Text)
    fichier_joint = Column(String(255))
    consentement = Column(Boolean, nullable=False)
    data_json = Column(JSON)

    def __repr__(self):
        return f"<Feedback {self.id} - {self.formation}>"