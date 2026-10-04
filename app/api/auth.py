from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.db.repositories.auth_repository import auth_repository

bearer = HTTPBearer(auto_error=False)


async def current_identity(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)) -> dict:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.", headers={"WWW-Authenticate": "Bearer"})
    identity = await auth_repository.get_user_for_token(credentials.credentials)
    if identity is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session is invalid or expired.", headers={"WWW-Authenticate": "Bearer"})
    user, session = identity
    return {"user": user, "session": session}
