# translates pure http --> group class

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from logging import Logger
from typing import List
from datetime import datetime, timedelta, timezone

from app.db.session import get_db
from app.db.schemas import GroupCreate, GroupJoinIn, GroupOut, GroupShortOut, GroupInviteOut
from app.db.models import Group, User, GroupMembers
from app.services.group_service import get_full_group_details, check_join_group, check_link_join, get_short_group_details, calculate_balance, add_user_group, create_group_invite_service
from app.core.exceptions import (
    GroupFullDetailsError, GroupCheckPwJoinError, GroupCheckLinkJoinError, GroupAddUserError, GroupShortDetailsError, 
    GroupInviteLinkCreateError, GroupNotFoundError, GroupUserAlreadyJoinedError
)
from app.core.security import get_current_user, get_current_group, GroupContext
from app.core.logger import get_request_logger


router = APIRouter()

@router.post("/create", response_model=GroupOut)
def create_group(
    group: GroupCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user), #from jwt
    logger: Logger = Depends(get_request_logger),
):
    try:
        logger.debug("group create payload received", extra={"group": group.dict(), "user_id": current_user.id})
        new_group = Group(pw=group.group_pw, name=group.name, emoji=group.emoji)

        # ensure the creator is attached through the association table
        new_member = GroupMembers(user=current_user, group=new_group)
        new_group.member_associations.append(new_member)

        db.add(new_group)
        db.commit()
        db.refresh(new_group)

        logger.info("group created", extra={"group_id": new_group.id})

        group_details = get_full_group_details(new_group.id, db=db)
        # calc balances
        for member in group_details.members:
            member.balance = calculate_balance(user=member, group_id=group_details.id, db=db)

        return group_details
    
    except GroupFullDetailsError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error polling db for group details"
        )
    except GroupNotFoundError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"error in create group endpoint: {e}")
        raise HTTPException(status_code=500, detail="Unexpected server error")

@router.post("/join", response_model=GroupOut)
def join_group(
    group: GroupJoinIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    logger: Logger = Depends(get_request_logger),
):
    try:
        logger.debug("join group attempt", extra={"type": group.pw_auth if group.pw_auth else group.link_auth})
        group_id = check_join_group(group_name=group.pw_auth.group_name, group_pw=group.pw_auth.group_pw, db=db) if group.pw_auth else check_link_join(token_link=group.link_auth, db=db)
        # group not found error raised instead of checking group_id val
        joined_group_details = add_user_group(group_id=group_id, user=current_user, db=db)
        db.commit()

        for member in joined_group_details.members:
            member.balance = calculate_balance(user=member, group_id=joined_group_details.id, db=db)
            # this is only querying, no db commit needed
        return joined_group_details

    except GroupNotFoundError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        ) 
    except GroupAddUserError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error adding user to group relationship"
        )
    except GroupUserAlreadyJoinedError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already are in this group"
        )
    except GroupCheckLinkJoinError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite link has already been used or is expired. Request another"
        ) 
    except GroupCheckPwJoinError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password or name"
        ) 
    except Exception as e:
        db.rollback()
        logger.error(f"error in join group endpoint: {e}")
        raise HTTPException(status_code=500, detail="Unexpected server error")


@router.get("/view-short", response_model=List[GroupShortOut])
def view_all_groups(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    logger: Logger = Depends(get_request_logger),
):
    try:
        logger.debug("view all groups attempt", extra={"User id": current_user.id, "User name ": current_user.name})
        return get_short_group_details(user_id=current_user.id, db=db)
    except GroupShortDetailsError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error finding user's groups"
        )
    except Exception as e:
        # no db rollback cause only reading
        raise HTTPException(status_code=500, detail="Unexpected server error")

@router.get("/{group_id}", response_model=GroupOut)
def view_group(
    ctx: GroupContext = Depends(get_current_group),
    db: Session = Depends(get_db),
    logger: Logger = Depends(get_request_logger),
):
    try:
        logger.debug("view group attempt", extra={"group_name": ctx.group.name, "user_name": ctx.user.name})
        
        joined_group_details = get_full_group_details(ctx.group.id, db=db)
        for member in joined_group_details.members:
            member.balance = calculate_balance(user=member, group_id=joined_group_details.id, db=db)
        return joined_group_details
    except GroupFullDetailsError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error polling db for group details"
        )
    except Exception as e:
        logger.error(f"error in view group endpoint: {e}")
        raise HTTPException(status_code=500, detail="Unexpected server error")
    

@router.get("/{group_id}/create-invite", response_model=GroupInviteOut)
def create_group_invite(
    ctx: GroupContext = Depends(get_current_group),
    db: Session = Depends(get_db),
    logger: Logger = Depends(get_request_logger)
):
    try:
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=10) #10 min token expiry time
        inv = create_group_invite_service(user_id=ctx.user.id, group_id=ctx.group.id, db=db, expires_at=expires_at)
        db.commit()
        return inv

    except GroupInviteLinkCreateError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating group invite"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating group invite: {e}")
        raise HTTPException(status_code=500, detail="Unexpected server error")
