from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel
from backend.database import SessionLocal, engine, Base
from backend.models import User, Product
from typing import Optional
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

# Initialize app
app = FastAPI()

app.mount("/static", StaticFiles(directory="backend/static"), name="static")
templates = Jinja2Templates(directory="backend/templates")

# Create tables
Base.metadata.create_all(bind=engine)


# Pydantic model for request body
class ProductCreate(BaseModel):
    name: str
    description: str
    price: int

@app.get("/", response_class=HTMLResponse)
def serve_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# API to add a new product
@app.post("/add-product")
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
@app.get("/get-products")
def get_products():
    db = SessionLocal()
    products = db.query(Product).all()
    db.close()
    return products


# Get single product by ID
@app.get("/product/{product_id}")
def get_single_product(product_id: int):
    db = SessionLocal()
    product = db.query(Product).filter(Product.id == product_id).first()
    db.close()
    if product:
        return product
    else:
        raise HTTPException(status_code=404, detail="Product not found")


# Delete product by ID
@app.delete("/delete-product/{product_id}")
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


# Pydantic model for product update
class ProductUpdate(BaseModel):
    id: int
    name: str
    description: str
    price: int

@app.put("/update-product")
def update_product(product: ProductUpdate):
    db = SessionLocal()
    product_to_update = db.query(Product).filter(Product.id == product.id).first()

    if product_to_update is None:
        db.close()
        raise HTTPException(status_code=404, detail="Product not found")

    # Update product fields
    product_to_update.name = product.name
    product_to_update.description = product.description
    product_to_update.price = product.price
    db.commit()
    db.refresh(product_to_update)
    db.close()

    return {"message": "Product updated successfully", "product": {
        "id": product_to_update.id,
        "name": product_to_update.name,
        "description": product_to_update.description,
        "price": product_to_update.price
    }}


# Pydantic model for partial product update
class ProductPartialUpdate(BaseModel):
    id: int
    updated_fields: dict

@app.patch("/update-product")
def partial_update_product(product: ProductPartialUpdate):
    db = SessionLocal()
    product_to_update = db.query(Product).filter(Product.id == product.id).first()

    if product_to_update is None:
        db.close()
        raise HTTPException(status_code=404, detail="Product not found")

    # Update only the fields provided in the payload
    for field, value in product.updated_fields.items():
        if hasattr(product_to_update, field):
            setattr(product_to_update, field, value)

    db.commit()
    db.refresh(product_to_update)
    db.close()

    return {"message": "Product partially updated", "product": {
        "id": product_to_update.id,
        "name": product_to_update.name,
        "description": product_to_update.description,
        "price": product_to_update.price
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


security = HTTPBasic()

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != "admin" or credentials.password != "password@1234":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


# Pydantic model for request body (username)
class UsernameDelete(BaseModel):
    username: str

# API endpoint to delete a specific user by username (from the request body)
@app.delete("/delete-user")
def delete_user(payload: UsernameDelete):
    db = SessionLocal()
    user_to_delete = db.query(User).filter(User.username == payload.username).first()

    if user_to_delete:
        db.delete(user_to_delete)
        db.commit()
        db.close()
        return {"message": f"User {payload.username} deleted successfully"}
    else:
        db.close()
        raise HTTPException(status_code=404, detail="User not found")


# API endpoint to delete all products, secured with basic auth
@app.delete("/clear-products")
def clear_products(user: str = Depends(get_current_user)):
    db = SessionLocal()

    # Delete all products
    db.query(Product).delete()
    db.commit()
    db.close()

    return {"message": "All products cleared from the database"}


# API endpoint to delete all users, secured with basic auth
@app.delete("/clear-users")
def clear_users(user: str = Depends(get_current_user)):
    db = SessionLocal()

    # Delete all users
    db.query(User).delete()
    db.commit()
    db.close()

    return {"message": "All users cleared from the database"}
