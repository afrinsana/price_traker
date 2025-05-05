from typing import List

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from starlette import status

from app.core.security import get_current_active_user
from app.crud.product import product_crud
from app.db.session import get_db
from app.schemas.product import Product, ProductCreate, ProductUpdate
from app.models.user import User
from app.tasks.price_checks import check_product_price

router = APIRouter()

@router.get("/", response_model=List[Product])
def read_products(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
):
    """Retrieve products for current user"""
    products = product_crud.get_multi_by_owner(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    return products

@router.post("/", response_model=Product)
def create_product(
    *,
    db: Session = Depends(get_db),
    product_in: ProductCreate,
    current_user: User = Depends(get_current_active_user),
    background_tasks: BackgroundTasks,
):
    """Create new product for current user"""
    # Check if product already exists
    existing_product = product_crud.get_by_url(db, url=product_in.url)
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this URL already exists"
        )
    
    product = product_crud.create_with_owner(
        db=db, obj_in=product_in, user_id=current_user.id
    )
    
    # Immediately trigger price check
    background_tasks.add_task(
        check_product_price.delay,
        product_id=product.id
    )
    
    return product

@router.put("/{product_id}", response_model=Product)
def update_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    product_in: ProductUpdate,
    current_user: User = Depends(get_current_active_user),
):
    """Update existing product"""
    product = product_crud.get(db, id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    if product.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    product = product_crud.update(db, db_obj=product, obj_in=product_in)
    return product

@router.delete("/{product_id}", response_model=Product)
def delete_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    current_user: User = Depends(get_current_active_user),
):
    """Delete existing product"""
    product = product_crud.get(db, id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    if product.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    product = product_crud.remove(db, id=product_id)
    return product

@router.post("/{product_id}/check", response_model=dict)
def trigger_price_check(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    current_user: User = Depends(get_current_active_user),
    background_tasks: BackgroundTasks,
):
    """Manually trigger price check for a product"""
    product = product_crud.get(db, id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    if product.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    background_tasks.add_task(
        check_product_price.delay,
        product_id=product.id
    )
    
    return {"message": "Price check initiated"}