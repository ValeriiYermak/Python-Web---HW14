from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar
from src.database.db import get_db
from src.entity.models import User
from src.schemas.user import UserSchema


async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    """
    The get_user_by_email function takes in an email and a database session, and returns the user with that email.
    :param email: str: Specify the type of the parameter to be a string or a string literal (e.g. "email")
    :param db: AsyncSession: Pass the database session to the function
    :return: A user object with the email passed in the parameter
    """
    stmt = select(User).filter_by(email=email)
    user = await db.execute(stmt)
    user = user.scalars().first()
    return user


async def create_user(body: UserSchema, db: AsyncSession = Depends(get_db)):
    """
    The create_user function creates a new user in the database.
    :param body: UserSchema: Get the data from the request body
    :param db: AsyncSession: Pass the database session to the function
    :return: A user object with the data from the request body
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as err:
        print(err)

    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: AsyncSession):
    """
    The update_token function updates the refresh token in the database.
    :param user: User: Pass the user object to the function
    :param token: str: Update the refresh token in the database
    :param db: AsyncSession: Pass the database session to the function
    :return: None
    """
    user.refresh_token = token
    await db.commit()


async def confirmed_email(email: str, db: AsyncSession) -> None:
    """
    The confirmed_email function updates the confirmed field in the database to True for a user with the given email.
    :param email: str: Get the email of the user that is confirmed
    :param db: AsyncSession: Pass the database session to the function
    :return: None
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()


async def update_avatar_url(email: str, url: str | None, db: AsyncSession)-> User:
    """
    The update_avatar_url function updates the avatar url in the database.
    :param email: str: Get the email of the user that is logged in
    :param url: str: Update the avatar url in the database
    :param db: AsyncSession: Pass the database session to the function
    :return: The user object with the new avatar url
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    await db.commit()
    await db.refresh(user)
    return user
