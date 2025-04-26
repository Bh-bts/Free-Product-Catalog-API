# main.py

from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

# Initialize app
app = FastAPI()

# Database setup
DATABASE_URL = "sqlite:///./products.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Product model
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    price = Column(Integer)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic model for request body
class ProductCreate(BaseModel):
    name: str
    description: str
    price: int


# API to add a new product
@app.post("/add_product/")
def add_product(product: ProductCreate):
    db = SessionLocal()
    # Check if product with the same name already exists
    existing_product = db.query(Product).filter(Product.name == product.name).first()

    if existing_product:
        db.close()
        return {"message": "Product already exists"}

    # If not exists, add new product
    new_product = Product(
        name=product.name,
        description=product.description,
        price=product.price
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    db.close()
    return {"message": "Product added successfully", "product": {
        "id": new_product.id,
        "name": new_product.name,
        "description": new_product.description,
        "price": new_product.price
    }}

# API endpoint to get all products
@app.get("/products/")
def get_products():
    db = SessionLocal()
    products = db.query(Product).all()
    db.close()
    return products

# Get single product by ID
@app.get("/products/{product_id}")
def get_single_product(product_id: int):
    db = SessionLocal()
    product = db.query(Product).filter(Product.id == product_id).first()
    db.close()
    if product:
        return product
    else:
        raise HTTPException(status_code=404, detail="Product not found")


# Delete product by ID
@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    db = SessionLocal()
    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        db.delete(product)
        db.commit()
        db.close()
        return {"message": "Product deleted successfully"}
    else:
        db.close()
        raise HTTPException(status_code=404, detail="Product not found")