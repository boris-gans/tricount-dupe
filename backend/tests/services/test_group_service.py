import pytest

from app.db.models import (
    Group,
    GroupMembers,
    User,
    Expense,
    ExpenseSplit,
    GroupInvite,
)
from app.services.group_service import (
    get_full_group_details,
    check_join_group,
    check_link_join,
    add_user_group,
    get_short_group_details,
    calculate_balance,
    create_group_invite_service,
)
from app.core.exceptions import (
    GroupFullDetailsError,
    GroupNotFoundError,
    GroupCheckLinkJoinError,
    GroupAddUserError,
    GroupShortDetailsError,
    GroupCalculateBalanceError,
    GroupInviteLinkCreateError,
)


def test_get_full_group_details_success(db_session):
    user = User(name="Greg", email="greg@example.com", pw="hashed")
    group = Group(name="Weekend", pw="pw", emoji="🏖")
    db_session.add_all([user, group])
    db_session.flush()

    membership = GroupMembers(user_id=user.id, group_id=group.id)
    db_session.add(membership)

    expense = Expense(
        amount=100.0,
        description="Hotel",
        group_id=group.id,
        paid_by_id=user.id,
        created_by_id=user.id,
    )
    db_session.add(expense)
    db_session.flush()

    split = ExpenseSplit(expense_id=expense.id, user_id=user.id, amount=100.0)
    db_session.add(split)
    db_session.flush()

    result = get_full_group_details(group_id=group.id, db=db_session)

    assert result.id == group.id
    assert len(result.members) == 1
    assert len(result.expenses) == 1


def test_get_full_group_details_failure(db_session, monkeypatch):
    def broken_query(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(db_session, "query", broken_query)

    with pytest.raises(GroupFullDetailsError):
        get_full_group_details(group_id=1, db=db_session)


def test_check_join_group_success(db_session):
    group = Group(name="Study", pw="joinme", emoji=None)
    db_session.add(group)
    db_session.flush()

    group_id = check_join_group(group_name="Study", group_pw="joinme", db=db_session)

    assert group_id == group.id


def test_check_join_group_failure(db_session, monkeypatch):
    def broken_query(*args, **kwargs):
        raise RuntimeError("db down")

    monkeypatch.setattr(db_session, "query", broken_query)

    with pytest.raises(GroupNotFoundError):
        check_join_group(group_name="Nope", group_pw="invalid", db=db_session)


def test_check_link_join_success(db_session):
    creator = User(name="Hank", email="hank@example.com", pw="hashed")
    group = Group(name="Picnic", pw="token", emoji=None)
    invite = GroupInvite(group_id=1, created_by_id=1, token="abc123")

    db_session.add_all([creator, group])
    db_session.flush()

    invite.group_id = group.id
    invite.created_by_id = creator.id
    db_session.add(invite)
    db_session.flush()

    group_id = check_link_join(token_link="https://example.com/join?token=abc123", db=db_session)

    assert group_id == group.id
    assert invite.used is True


def test_check_link_join_expired(db_session):
    creator = User(name="Ian", email="ian@example.com", pw="hashed")
    group = Group(name="Retreat", pw="pw", emoji=None)
    invite = GroupInvite(group=group, created_by=creator, token="expired")
    invite.used = True

    db_session.add_all([creator, group, invite])
    db_session.flush()

    with pytest.raises(GroupCheckLinkJoinError):
        check_link_join(token_link="https://example.com/join?token=expired", db=db_session)


def test_add_user_group_success(db_session):
    user = User(name="Jane", email="jane@example.com", pw="hashed")
    group = Group(name="Brunch", pw="pw", emoji=None)
    db_session.add_all([user, group])
    db_session.flush()

    result = add_user_group(group_id=group.id, user=user, db=db_session)

    assert any(member.id == user.id for member in result.members)


def test_add_user_group_failure(db_session, monkeypatch):
    user = User(name="Kyle", email="kyle@example.com", pw="hashed")
    group = Group(name="Hike", pw="pw", emoji=None)
    db_session.add_all([user, group])
    db_session.flush()

    def broken_flush(*args, **kwargs):
        raise RuntimeError("cannot flush")

    monkeypatch.setattr(db_session, "flush", broken_flush)

    with pytest.raises(GroupAddUserError): #not sure why this exception is not being raised
        add_user_group(group_id=group.id, user=user, db=db_session)


def test_get_short_group_details_success(db_session):
    user = User(name="Liam", email="liam@example.com", pw="hashed")
    group = Group(name="Cycling", pw="pw", emoji=None)
    db_session.add_all([user, group])
    db_session.flush()

    membership = GroupMembers(user_id=user.id, group_id=group.id)
    db_session.add(membership)
    db_session.flush()

    groups = get_short_group_details(user_id=user.id, db=db_session)

    assert len(groups) == 1
    assert groups[0].id == group.id


def test_get_short_group_details_failure(db_session, monkeypatch):
    def broken_query(*args, **kwargs):
        raise RuntimeError("query failed")

    monkeypatch.setattr(db_session, "query", broken_query)

    with pytest.raises(GroupShortDetailsError):
        get_short_group_details(user_id=1, db=db_session)


def test_calculate_balance_success(db_session):
    user = User(name="Mia", email="mia@example.com", pw="hashed")
    partner = User(name="Ned", email="ned@example.com", pw="hashed")
    group = Group(name="Ski", pw="pw", emoji=None)
    db_session.add_all([user, partner, group])
    db_session.flush()

    expense = Expense(
        amount=120.0,
        description="Lift tickets",
        group_id=group.id,
        paid_by_id=user.id,
        created_by_id=user.id,
    )
    db_session.add(expense)
    db_session.flush()

    split_user = ExpenseSplit(expense_id=expense.id, user_id=user.id, amount=40.0)
    split_partner = ExpenseSplit(expense_id=expense.id, user_id=partner.id, amount=80.0)
    db_session.add_all([split_user, split_partner])
    db_session.flush()

    balance = calculate_balance(user=user, group_id=group.id, db=db_session)

    assert balance == pytest.approx(80.0)


def test_calculate_balance_failure(db_session, monkeypatch):
    def broken_query(*args, **kwargs):
        raise RuntimeError("sum failed")

    monkeypatch.setattr(db_session, "query", broken_query)

    with pytest.raises(GroupCalculateBalanceError):
        calculate_balance(user=User(id=1, name="Temp", email="t@example.com", pw="pw"), group_id=1, db=db_session)


def test_create_group_invite_service_success(db_session):
    user = User(name="Olive", email="olive@example.com", pw="hashed")
    group = Group(name="Potluck", pw="pw", emoji=None)
    db_session.add_all([user, group])
    db_session.flush()

    invite = create_group_invite_service(user_id=user.id, group_id=group.id, db=db_session)

    assert invite.group_id == group.id
    assert invite.created_by_id == user.id
    assert invite.token
