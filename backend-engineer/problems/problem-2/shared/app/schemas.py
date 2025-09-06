from pydantic import BaseModel, EmailStr
from typing import List, Optional

# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    model_config = {'from_attributes': True}

# --- Product Schemas ---
class ProductBase(BaseModel):
    name: str
    price: float

class ProductCreate(ProductBase):
    quantity: int

class Product(ProductBase):
    id: int
    quantity: int
    model_config = {'from_attributes': True}

# --- Order Schemas ---
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]

class Order(BaseModel):
    id: int
    user_id: int
    total_price: float
    status: str
    items: List[OrderItemCreate] = []
    model_config = {'from_attributes': True}

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str