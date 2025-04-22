from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, Session, declarative_base

# Database configuration 
DATABASE_URL = "sqlite:///./test.db" 

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    productions = relationship("Production", back_populates="product")

class Line(Base):
    __tablename__ = "lines"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    productions = relationship("Production", back_populates="line")

class Shift(Base):
    __tablename__ = "shifts"
    id = Column(Integer, primary_key=True, index=True)
    shift_name = Column(String, index=True)
    productions = relationship("Production", back_populates="shift")

class Production(Base):
    __tablename__ = "production"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    line_id = Column(Integer, ForeignKey("lines.id"))
    shift_id = Column(Integer, ForeignKey("shifts.id"))
    quantity = Column(Integer)
    energy_consumed = Column(Float)
    line_speed = Column(Float)

    product = relationship("Product", back_populates="productions")
    line = relationship("Line", back_populates="productions")
    shift = relationship("Shift", back_populates="productions")


def init_db():
    Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/products/")
def create_product(name: str, db: Session = Depends(get_db)):
    db_product = Product(name=name)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.post("/production/")
def create_production(
    product_id: int,
    line_id: int,
    shift_id: int,
    quantity: int,
    energy_consumed: float,
    line_speed: float,
    db: Session = Depends(get_db),
):
    db_production = Production(
        product_id=product_id,
        line_id=line_id,
        shift_id=shift_id,
        quantity=quantity,
        energy_consumed=energy_consumed,
        line_speed=line_speed
    )
    db.add(db_production)
    db.commit()
    db.refresh(db_production)
    return db_production

@app.get("/dashboard/")
def get_dashboard(db: Session = Depends(get_db)):
    productions = db.query(Production).all()
    total_quantity = sum(p.quantity for p in productions)
    total_energy = sum(p.energy_consumed for p in productions)
    avg_line_speed = sum(p.line_speed for p in productions) / len(productions) if productions else 0
    return {
        "total_production_quantity": total_quantity,
        "total_energy_consumed": total_energy,
        "average_line_speed": avg_line_speed,
        "entries": productions
    }


