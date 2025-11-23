# logic for creating groups; eg. only unique users per group, max amount, etc.
import secrets
from datetime import datetime, timezone

from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from urllib.parse import urlparse, parse_qs

from app.db.models import Group, Expense, ExpenseSplit, User, GroupMembers, GroupInvite
from app.db.schemas import GroupOut, GroupShortOut, GroupInviteOut
from app.core.exceptions import (
    GroupFullDetailsError, GroupCalculateBalanceError, GroupCheckPwJoinError, GroupCheckLinkJoinError, 
    GroupAddUserError, GroupShortDetailsError, GroupInviteLinkCreateError, GroupNotFoundError, GroupUserAlreadyJoinedError
)
from app.core.logger import get_module_logger


logger = get_module_logger(__name__)


def get_full_group_details(group_id: int, db: Session) -> GroupOut:
    try:
        group_details = (
            db.query(Group)
            .options(
                joinedload(Group.members),
                joinedload(Group.expenses)
                .joinedload(Expense.splits)
                .joinedload(ExpenseSplit.user),
                # paid_by intentionally lazy-loaded to keep response size small
            )
            .filter(Group.id == group_id)
            .first()
        )

        logger.debug("group details loaded", extra={"group_id": group_id})

        if not group_details:
            logger.warning("group lookup failed", extra={"group_id": group_id})
            raise GroupNotFoundError

        return group_details
    except GroupNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error loading group details: {e}")
        raise GroupFullDetailsError from e

def check_join_group(group_name: str, group_pw: str, db: Session) -> int:
    try:
        group = (
            db.query(Group)
            .filter(Group.name == group_name)
            .filter(Group.pw == group_pw)
            .first()
        )

        if not group:
            logger.warning("group lookup failed", extra={"group_name": group_name})
            raise GroupCheckPwJoinError
        return group.id

    except GroupCheckPwJoinError:
        raise
    except Exception as e:
        logger.error(f"Error checking join group: {e}")
        raise GroupNotFoundError from e
    

def check_link_join(token_link: str, db: Session) -> int:
    try:
        parsed = urlparse(token_link)
        query_params = parse_qs(parsed.query)
        token = query_params.get("token", [None])[0]

        logger.info(f"Token to check: {token}")

        invite = (
            db.query(GroupInvite)
            .filter(GroupInvite.token == token)
            .first()
        )


        if not invite or invite.used or (invite.expires_at and invite.expires_at < datetime.now(timezone.utc)):
            raise GroupCheckLinkJoinError

        #mark as used
        invite.used = True
        db.add(invite)
        db.flush()
        db.refresh(invite)
        return invite.group_id

    except Exception as e:
        db.rollback() #cause we change used field
        logger.error(f"Error checking link join: {e}")
        raise GroupCheckLinkJoinError from e

def add_user_group(group_id: int, user: User, db: Session) -> GroupOut:
    try:
        group = (
            db.query(Group)
            .filter(Group.id == group_id)
            .first()
        )
        if not group:
            logger.warning("group not found when adding user", extra={"group_id": group_id, "user_id": user.id})
            raise GroupNotFoundError

        new_member = GroupMembers(user=user, group=group)
        group.member_associations.append(new_member)

        db.add(new_member)
        db.flush() #best practice; only commit and rollback endpoint as it owns request lifecycle
        db.refresh(new_member)
        return get_full_group_details(group_id=group_id, db=db)
    except IntegrityError:
        logger.error("User already added to group")
        raise GroupUserAlreadyJoinedError
    except Exception as e:
        logger.error(f"Error adding user to group: {e}")
        raise GroupAddUserError from e


def get_short_group_details(user_id: int, db: Session) -> list[GroupShortOut]:
    try:
        logger.debug("group list request received")
        group_list = (
            db.query(Group)
            .join(Group.members)
            .filter(User.id == user_id)
            .all()
        )
        logger.debug("group short list loaded", extra={"User_id": user_id})
        return group_list
    except Exception as e:
        logger.error(f"Error getting short group list: {e}")
        raise GroupShortDetailsError from e

def calculate_balance(user: User, group_id: int, db: Session):
    try:
        #total paid by user_id in this group
        total_paid = (
            db.query(func.coalesce(func.sum(Expense.amount), 0.0))
            .filter(Expense.group_id == group_id, Expense.paid_by_id == user.id)
            .scalar()
        )

        #total owed by the user in this group (splits)
        total_owed = (
            db.query(func.coalesce(func.sum(ExpenseSplit.amount), 0.0))
            .join(Expense)
            .filter(Expense.group_id == group_id, ExpenseSplit.user_id == user.id)
            .scalar()
        )

        balance = float(total_paid) - float(total_owed)
        return balance

    except Exception as e:
        logger.error(f"Error in calculate balance service: {e}")
        raise GroupCalculateBalanceError from e

def create_group_invite_service(user_id: int, group_id: int, db: Session, expires_at=None) -> GroupInviteOut:
    try:
        token = secrets.token_urlsafe(16)
        invite = GroupInvite(
            group_id=group_id,
            created_by_id=user_id,
            token=token,
            expires_at=expires_at
        )
        db.add(invite)
        db.flush()
        db.refresh(invite)
        return invite

    except Exception as e:
        db.rollback()
        logger.error(f"Error in group invite service: {e}")
        raise GroupInviteLinkCreateError from e
