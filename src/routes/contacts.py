from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.entity.models import User, Role
from src.repository import contacts as repository_contacts
from src.schemas.contacts import ContactResponse, ContactUpdateSchema, \
    ContactSchema
from typing import List, Optional
from src.services.auth import auth_service
from src.services.roles import RoleAccess

router = APIRouter(prefix="/contacts", tags=["contacts"])

access_to_route_all = RoleAccess([Role.admin, Role.moderator])


@router.get("/", response_model=List[ContactResponse],
            response_model_exclude_unset=True)
async def get_contacts(limit: int = Query(default=10, ge=10, le=500),
                       offset: int = Query(default=0, ge=0),
                       query: Optional[str] = None,
                       db: AsyncSession = Depends(get_db),
                       user: User = Depends(auth_service.get_current_user)):
    """
    The get_contacts function returns a list of contacts for a given user.
    :param limit:
    :param offset:
    :param query:
    :param db:
    :param user:
    :return:
    """
    contacts = await repository_contacts.get_contacts(limit, offset, query,
                                                      db, user)
    return contacts


@router.get("/all", response_model=List[ContactResponse],
            dependencies=[Depends(access_to_route_all)])
async def get_all_contacts(limit: int = Query(default=10, ge=10, le=500),
                           offset: int = Query(default=0, ge=0),
                           query: Optional[str] = None,
                           db: AsyncSession = Depends(get_db),
                           user: User = Depends(auth_service.get_current_user)):
    """
    The get_all_contacts function returns a list of all contacts.
    :param limit:
    :param offset:
    :param query:
    :param db:
    :param user:
    :return:
    """
    contacts = await repository_contacts.get_all_contacts(limit, offset, query,
                                                          db)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: int = Path(ge=1),
                      db: AsyncSession = Depends(get_db),
                      user: User = Depends(auth_service.get_current_user)):
    """
    The get_contact function returns the contact with the given contact_id.
    :param contact_id: int: Specify the id of the contact to get from the database
    :param db: AsyncSession: Pass the database session
    :param user: User: Get the user from the database
    :return: A contact object with the given id from the database
    """
    contact = await repository_contacts.get_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Contact not found")
    return contact


@router.post("/", response_model=ContactResponse,
             status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactSchema,
                         db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
    The create_contact function creates a new contact in the database.
    :param body: ContactSchema: Get the data from the request body
    :param db: AsyncSession: Pass the database session
    :param user: User: Get the user from the database
    :return: A contact object
    """
    contact = await repository_contacts.create_contact(body, db, user)
    return contact


@router.put("/{contact_id}")
async def update_contact(body: ContactUpdateSchema,
                         contact_id: int = Path(ge=1),
                         db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
    The update_contact function updates a contact in the database.
    :param contact_id: int: Specify the id of the contact to be updated in the database
    :param body: ContactUpdateSchema: Pass the data to be updated in the database
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the user from the database
    :return: A contact object with the updated data from the database
    """
    contact = await repository_contacts.update_contact(contact_id, body, db,
                                                       user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Contact not found")
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int = Path(ge=1),
                         db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
    The delete_contact function deletes a contact from the database.
    :param contact_id: int: Specify the id of the contact to be deleted from the database
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the user from the database
    :return: A contact object with the given id from the database
    """
    contact = await repository_contacts.get_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Contact not found")
    contact = await repository_contacts.delete_contact(contact_id, db, user)
    return contact

#
# @router.get("/birthdays", response_model=List[ContactResponse])
# async def get_upcoming_birthdays(db: AsyncSession = Depends(get_db)):
#     contacts = await repository_contacts.get_upcoming_birthdays(db)
#     return contacts
