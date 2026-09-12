from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import create_access_token

router = APIRouter()

@router.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # In a real system, we'd query the DB for the officer's credentials
    # For this mock, we accept any dummy credentials if username is provided
    if not form_data.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    badge_number = form_data.username # using username field for badge_number
    access_token = create_access_token(
        subject=badge_number,
        role="ANALYST"
    )
    
    return {"access_token": access_token, "token_type": "bearer", "role": "ANALYST"}
