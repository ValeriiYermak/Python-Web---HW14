from datetime import datetime, timedelta, date
from typing import List

from sqlalchemy import select, func, cast, String
from sqlalchemy.ext.asyncio import AsyncSession
from src.entity.models import Contact, User
from src.schemas.contacts import ContactUpdateSchema, ContactSchema


async def get_contacts(limit: int, offset: int, query: str, db: AsyncSession,
                       user: User):
    """
    The get_contacts function returns a list of contacts for a given user.
    :param user: User: Get the user from the database
    :param limit: int: Limit the number of contacts returned
    :param offset: int: Skip a certain number of contacts
    :param query: str: Filter the contacts by name, lastname or email
    :param db: AsyncSession: Access the database
    :param user: User: Get the user from the database
    :return: A list of contacts for the given user
    """
    stmt = select(Contact).filter_by(user=user).offset(offset).limit(limit)
    if query:
        stmt = stmt.filter(
            (Contact.name.ilike(f"%{query}%")) |
            (Contact.lastname.ilike(f"%{query}%")) |
            (Contact.email.ilike(f"%{query}%"))
        )
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_all_contacts(limit: int, offset: int, query: str,
                           db: AsyncSession):
    """
    The get_all_contacts function returns a list of all contacts.

    :param limit: int: Limit the number of contacts returned
    :param offset: int: Skip a certain number of contacts
    :param query: str: Filter the contacts by name, lastname or email
    :param db: AsyncSession: Access the database
    :return: A list of contacts for the given user
    """
    stmt = select(Contact).offset(offset).limit(limit)
    if query:
        stmt = stmt.filter(
            (Contact.name.ilike(f"%{query}%")) |
            (Contact.lastname.ilike(f"%{query}%")) |
            (Contact.email.ilike(f"%{query}%"))
        )
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession, user: User):
    """
    The get_contact function returns the contact with the given contact_id.

    :param contact_id: int: Specify the id of the contact to get from the database
    :param db: AsyncSession: Pass the database session
    :param user: User: Get the user from the database
    :return: A contact object with the given id from the database
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    contact = await db.execute(stmt)
    return contact.scalars().first()


async def create_contact(body: ContactSchema, db: AsyncSession, user: User):
    """
    The create_contact function creates a new contact in the database.

    :param body: ContactSchema: Get the data from the request body
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the user from the database
    :return: A contact object with the new data from the request body
    """
    contact = Contact(**body.model_dump(exclude_unset=True), user=user)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactUpdateSchema,
                         db: AsyncSession, user: User):
    """
    The update_contact function updates a contact in the database.

    :param contact_id: int: Specify the id of the contact to be updated in the database
    :param body: ContactUpdateSchema: Pass the data to be updated in the database
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the user from the database
    :return: A contact object with the updated data from the database
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(stmt)
    contact = result.scalars().first()
    if contact:
        contact.name = body.name
        contact.lastname = body.lastname
        contact.email = body.email
        contact.phone = body.phone
        contact.birthdate = body.birthdate
        contact.others_info = body.others_info
        contact.completed = body.completed
        await db.commit()
        await db.refresh(contact)
    return contact
    pass


async def delete_contact(contact_id: int, db: AsyncSession, user: User):
    """
    The delete_contact function deletes a contact from the database.
    :param contact_id: int: Specify the id of the contact to be deleted from the database
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the user from the database
    :return: A contact object with the given id from the database
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    contact = await db.execute(stmt)
    contact = contact.scalars().first()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact

# async def get_upcoming_birthdays(db: AsyncSession, user: User):
#     today = datetime.now().date()
#     next_week = today + timedelta(days=7)
#     stmt = select(Contact).filter(
#         func.DATE_FORMAT(cast(Contact.birthdate, String),
#                          "%d.%m") >= func.DATE_FORMAT(today, "%d.%m"),
#         func.DATE_FORMAT(cast(Contact.birthdate, String),
#                          "%d.%m") <= func.DATE_FORMAT(next_week, "%d.%m"))
#     contacts = await db.execute(stmt)
#     upcoming_birthdays = []
#     for contact in contacts.scalars().all():
#         # Convert birthdate from string to date format
#         birthdate = datetime.strptime(contact.birthdate, "%d.%m.%Y").date()
#         contact_dict = contact.__dict__
#         contact_dict["birthdate"] = birthdate
#         upcoming_birthdays.append(contact_dict)
#
#     return upcoming_birthdays
