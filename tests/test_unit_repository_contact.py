import unittest
from unittest.mock import MagicMock, AsyncMock, Mock

from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Contact, User
from src.schemas.contacts import ContactSchema, ContactUpdateSchema
from src.repository.contacts import get_contacts, get_all_contacts, create_contact, update_contact, delete_contact, get_contact


class TestAsyncContact(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.session = AsyncMock(spec=AsyncSession)
        self.user = User(id=1, username='test_user', password='test_password', confirmed=True)

    async def get_all_contacts(self):
        limit = 10
        offset = 0
        contacts = [
            Contact(
                id=1,
                name='test_username_1',
                lastname='test_description_1',
                email='test_email_1@test.com',
                phone='1234567890',
                birthdate='test_birthdate_1',
                others_info='test_others_info_1',
                completed=True,
                created_at='2024-04-22T12:00:00',
                updated_at='2024-04-22T12:00:00',
                user=self.user
            ),
            Contact(
                id=2,
                name='test_username_2',
                lastname='test_description_2',
                email='test_email_2@test.com',
                phone='1234555890',
                birthdate='test_birthdate_2',
                others_info='test_others_info_2',
                completed=True,
                created_at='2024-04-22T12:00:00',
                updated_at='2024-04-22T12:00:00',
                user=self.user
            )
        ]
        mocked_contacts = Mock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_contact(limit, offset, self.session, self.user)
        self.assertEqual(result, contacts)

    async def test_create_contact(self):
        body = ContactSchema(
            name='test_username',
            lastname='test_description',
            email='test_email@test.com',
            phone='1234567890',
            birthdate='test_birthdate',
            others_info='test_others_info',
            completed=True
        )
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = None
        self.session.execute.return_value = mocked_contact
        result = await create_contact(body, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.name, body.name)
        self.assertEqual(result.lastname, body.lastname)

    # async def test_update_contact(self):
    #     body = ContactUpdateSchema(
    #         name='test_username',
    #         lastname='test_description',
    #         email='test_email@test.com',
    #         phone='1234567890',
    #         birthdate='test_birthdate',
    #         others_info='test_others_info',
    #         completed=True
    #     )
    #     mocked_contact = MagicMock()
    #     mocked_contact.scalar_one_or_none.return_value = Contact(
    #         id=1,
    #         name='test_username',
    #         lastname='test_description',
    #         email='test_email@test.com',
    #         phone='1234567890',
    #         birthdate='test_birthdate',
    #         others_info='test_others_info',
    #         completed=True
    #     )
    #     self.session.execute.return_value = mocked_contact
    #     result = await update_contact(1, body, self.session, self.user)
    #     self.assertIsInstance(result, Contact)
    #     self.assertEqual(result.name, body.name)
    #
    # async def test_delete_contact(self):
    #     mocked_contact = MagicMock()
    #     mocked_contact.scalar_one_or_none.return_value = Contact(id=1,
    #                                                              username='test_username',
    #                                                              description='test_description',
    #                                                              user=self.user)
    #     self.session.execute.return_value = mocked_contact
    #     result = await delete_contact(1, self.session, self.user)
    #     self.session.delete.assert_called_once()
    #     self.session.commit.assert_called_once()
    #
    #     self.assertIsInstance(result, Contact)
