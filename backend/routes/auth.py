"""Google Sign-In Authentication Routes"""
import os
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, status
from google.auth.transport import requests
from google.oauth2 import id_token

router = APIRouter()

# Google OAuth Configuration
GOOGLE_WEB_CLIENT_ID = os.getenv(
    "GOOGLE_WEB_CLIENT_ID",
    "YOUR_WEB_CLIENT_ID.apps.googleusercontent.com"
)


class GoogleTokenRequest(BaseModel):
    """Request body for Google token validation"""
    idToken: str


class GoogleAuthResponse(BaseModel):
    """Response body after successful Google authentication"""
    success: bool
    message: str
    user: dict
    sessionToken: str


@router.post("/google", response_model=GoogleAuthResponse)
async def authenticate_google(request: GoogleTokenRequest) -> GoogleAuthResponse:
    """
    Validate Google ID Token and return session token.

    - Receives: idToken from google_sign_in (client)
    - Validates: Token signature and aud (audience claim)
    - Extracts: Email and name from token
    - Returns: Mock session token (ready for future DB integration)
    """
    try:
        # Validate ID token signature and get claims
        claims = id_token.verify_oauth2_token(
            request.idToken,
            requests.Request(),
            GOOGLE_WEB_CLIENT_ID
        )

        # Verify token is not expired (verify_oauth2_token already checks this)
        # Verify audience matches our app
        if claims.get("aud") != GOOGLE_WEB_CLIENT_ID:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token audience does not match"
            )

        # Extract user information
        email = claims.get("email")
        name = claims.get("name")
        picture = claims.get("picture")

        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not found in token"
            )

        # TODO: Future implementation - check/create user in SQLite database
        # user = db.query(User).filter(User.email == email).first()
        # if not user:
        #     user = User(email=email, name=name, picture=picture)
        #     db.add(user)
        #     db.commit()

        # Generate mock session token (UUID v4)
        session_token = str(uuid.uuid4())

        return GoogleAuthResponse(
            success=True,
            message="Authentication successful",
            user={
                "email": email,
                "name": name,
                "picture": picture,
                "authenticatedAt": datetime.utcnow().isoformat()
            },
            sessionToken=session_token
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication error: {str(e)}"
        )
