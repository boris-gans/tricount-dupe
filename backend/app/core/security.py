# for later; jwt + pw hashing
from fastapi import HTTPException, Depends, status
from passlib.context import CryptContext
from datetime import datetime, timezone, timedelta
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import jwt, ExpiredSignatureError, JWTError
from dataclasses import dataclass

from app.core.config import settings
from app.db.session import get_db
from app.db.models import User, Group, GroupMembers


#inits
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer() 

@dataclass
class GroupContext:
    group: Group
    user: User


# basic hashing
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)

# jwt
def create_access_token(user_id: str | int):
    expire_d = settings.jwt_expiration_minutes
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=expire_d)
    to_encode = {"exp": expire, "sub": str(user_id)} #always gonna use user_id for subject
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

def decode_access_token(token: str):
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm], options={"verify_exp": True})
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# dependency for jwt
def get_current_user(
        creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        db: Session = Depends(get_db),
) -> User:
    """
        Because this is a dependency it needs a HTTPException rather than a custom exception. 
        This ensures fastapi stops the request immediatley and endpoints dont get called
    """
    payload = decode_access_token(creds.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    user = db.get(User, int(user_id))
    if not user:
        raise HTTPException(status_code=403, detail="User not found / doesn't exist")
    
    return user #since this is for internal use only, fine to return entire user object


# dependency using jwt and parameter group id
def get_current_group(
        group_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
) -> GroupContext: #verifying that User is part of Group
    """
        Because this is a dependency it needs a HTTPException rather than a custom exception. 
        This ensures fastapi stops the request immediatley and endpoints dont get called
    """

    group = (
        db.query(Group)
        .join(Group.member_associations)  # join groups to group_members
        .filter(
            Group.id == group_id,
            GroupMembers.user_id == current_user.id
        )
        .first()
    )

    if not group:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have access to this group",
        )

    return GroupContext(group=group, user=current_user)
