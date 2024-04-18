from unittest.mock import Mock, patch

import pytest

from src.schemas.contacts import ContactUpdateSchema
from src.services.auth import auth_service


def test_get_contacts(client, get_token):
    with patch.object(auth_service, "cache") as redis_mock:
        redis_mock.get.return_value = None
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("api/contacts", headers=headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == 0


def test_get_contact(client, get_token):
    with patch.object(auth_service, "cache") as redis_mock:
        redis_mock.get.return_value = None
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("api/contacts", headers=headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == 0


def test_create_contact(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("api/contacts", headers=headers, json={
            "name": "John",
            "lastname": "Doe",
            "email": "john.doe@example.com",
            "phone": "1234567",
            "birthdate": "01.01.1990",
            "others_info": "Some additional info",
            "completed": True
        })

        assert response.status_code == 201, response.text
        data = response.json()
        assert "id" in data
        assert data["name"] == "John"
        assert data["lastname"] == "Doe"
        assert data["email"] == "john.doe@example.com"
        assert data["phone"] == "1234567"
        assert data["birthdate"] == "01.01.1990"
        assert data["others_info"] == "Some additional info"


def test_update_contact(client, get_token):
    with patch.object(auth_service, "cache") as redis_mock:
        redis_mock.get.return_value = None
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.put("api/contacts/1", headers=headers, json={
            "name": "NIKO",
            "lastname": "ARMANY",
            "email": "new_ARMANY@example.com",
            "phone": "123456789",
            "birthdate": "01.01.1990",
            "others_info": "is None",
            "completed": False
        })
        assert response.status_code == 200, response.text
        data = response.json()
        assert "id" in data
        assert data["name"] == "NIKO"
        assert data["lastname"] == "ARMANY"
        assert data["email"] == "new_ARMANY@example.com"
        assert data["phone"] == "123456789"
        assert data["birthdate"] == "01.01.1990"
        assert data["others_info"] == "is None"
        assert data["completed"] is False


def test_delete_contact(client, get_token):
    with patch.object(auth_service, "cache") as redis_mock:
        redis_mock.get.return_value = None
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.delete("api/contacts/1", headers=headers)
        assert response.status_code == 204
