from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel
from backend.database import SessionLocal, engine, Base
from backend.models import User, Product
from typing import Optional

# Initialize app
app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)


# Pydantic model for request body
class ProductCreate(BaseModel):
    name: str
    description: str
    price: int


# API to add a new product
@app.post("/add_product")
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
@app.get("/products")
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


# PUT - Full update
@app.put("/products/{product_id}")
def update_product(product_id: int, updated_product: ProductCreate):
    db = SessionLocal()
    product = db.query(Product).filter(Product.id == product_id).first()

    if product is None:
        db.close()
        raise HTTPException(status_code=404, detail="Product not found")

    product.name = updated_product.name
    product.description = updated_product.description
    product.price = updated_product.price
    db.commit()
    db.refresh(product)
    db.close()
    return {"message": "Product updated successfully", "product": {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price
    }}


# PATCH - Partial update
@app.patch("/products/{product_id}")
def partial_update_product(product_id: int, updated_fields: dict):
    db = SessionLocal()
    product = db.query(Product).filter(Product.id == product_id).first()

    if product is None:
        db.close()
        raise HTTPException(status_code=404, detail="Product not found")

    for field, value in updated_fields.items():
        if hasattr(product, field):
            setattr(product, field, value)

    db.commit()
    db.refresh(product)
    db.close()
    return {"message": "Product partially updated", "product": {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price
    }}

class UserCreate(BaseModel):
    username: str
    password: Optional[str] = None

@app.post("/register")
def register_user(user: UserCreate):
    if not user.password:
        raise HTTPException(status_code=400, detail="Missing password")

    db = SessionLocal()
    existing_user = db.query(User).filter(User.username == user.username).first()

    if existing_user:
        db.close()
        return {"message": "Username already exists"}

    new_user = User(
        username=user.username,
        password=user.password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.close()
    return {"message": "User registered successfully", "user": {
        "id": new_user.id,
        "username": new_user.username
    }}


@app.post("/login")
def login_user(user: UserCreate):
    if not user.password:
        raise HTTPException(status_code=400, detail="Missing password")

    db = SessionLocal()
    existing_user = db.query(User).filter(User.username == user.username).first()

    if existing_user and existing_user.password == user.password:
        db.close()
        return {"message": "Login successful"}
    else:
        db.close()
        return {"message": "Invalid username or password"}
