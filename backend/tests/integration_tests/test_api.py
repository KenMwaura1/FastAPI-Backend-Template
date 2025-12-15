import pytest
from httpx import AsyncClient
import asyncio

# A workaround for the "Task attached to a different loop" error
# @pytest.fixture(scope="session")
# def event_loop():
#     try:
#         loop = asyncio.get_running_loop()
#     except RuntimeError:
#         loop = asyncio.new_event_loop()
#     yield loop
#     loop.close()


@pytest.mark.asyncio
async def test_signup(async_client: AsyncClient):
    # Test successful signup
    response = await async_client.post(
        "/api/auth/signup",
        json={"username": "testuser", "email": "test@example.com", "password": "password"},
    )
    assert response.status_code == 201
    assert "token" in response.json()["authorizedAccount"]

    # Test signup with existing username
    response = await async_client.post(
        "/api/auth/signup",
        json={"username": "testuser", "email": "another@example.com", "password": "password"},
    )
    assert response.status_code == 400

    # Test signup with existing email
    response = await async_client.post(
        "/api/auth/signup",
        json={"username": "anotheruser", "email": "test@example.com", "password": "password"},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_signin(async_client: AsyncClient):
    # First, create a user to sign in with
    await async_client.post(
        "/api/auth/signup",
        json={"username": "signinuser", "email": "signin@example.com", "password": "password"},
    )

    # Test successful signin
    response = await async_client.post(
        "/api/auth/signin",
        json={"username": "signinuser", "email": "signin@example.com", "password": "password"},
    )
    assert response.status_code == 202
    assert "token" in response.json()["authorizedAccount"]

    # Test signin with wrong password
    response = await async_client.post(
        "/api/auth/signin",
        json={"username": "signinuser", "email": "signin@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 400

    # Test signin with wrong username
    response = await async_client.post(
        "/api/auth/signin",
        json={"username": "wronguser", "email": "signin@example.com", "password": "password"},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_account(async_client: AsyncClient):
    # Create a user and get a token
    signup_response = await async_client.post(
        "/api/auth/signup",
        json={"username": "getuser", "email": "get@example.com", "password": "password"},
    )
    token = signup_response.json()["authorizedAccount"]["token"]
    user_id = signup_response.json()["id"]

    # Test get account with valid token
    response = await async_client.get(
        f"/api/accounts/{user_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["id"] == user_id

    # Test get account with invalid token
    response = await async_client.get(
        f"/api/accounts/{user_id}", headers={"Authorization": "Bearer invalidtoken"}
    )
    assert response.status_code == 401

    # Create a second user
    second_signup_response = await async_client.post(
        "/api/auth/signup",
        json={"username": "seconduser", "email": "second@example.com", "password": "password"},
    )
    second_user_id = second_signup_response.json()["id"]

    # Test get another user's account
    response = await async_client.get(
        f"/api/accounts/{second_user_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_account(async_client: AsyncClient):
    # Create a user and get a token
    signup_response = await async_client.post(
        "/api/auth/signup",
        json={"username": "updateuser", "email": "update@example.com", "password": "password"},
    )
    token = signup_response.json()["authorizedAccount"]["token"]
    user_id = signup_response.json()["id"]

    # Test update account with valid token
    response = await async_client.patch(
        f"/api/accounts/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"username": "updateduser"},
    )
    assert response.status_code == 200
    assert response.json()["authorizedAccount"]["username"] == "updateduser"

    # Test update account with invalid token
    response = await async_client.patch(
        f"/api/accounts/{user_id}",
        headers={"Authorization": "Bearer invalidtoken"},
        json={"username": "updateduser2"},
    )
    assert response.status_code == 401

    # Create a second user
    second_signup_response = await async_client.post(
        "/api/auth/signup",
        json={"username": "secondupdateuser", "email": "secondupdate@example.com", "password": "password"},
    )
    second_user_id = second_signup_response.json()["id"]

    # Test update another user's account
    response = await async_client.patch(
        f"/api/accounts/{second_user_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"username": "updateduser3"},
    )
    assert response.status_code == 403

    # Test update password and login with new password
    response = await async_client.patch(
        f"/api/accounts/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"password": "newpassword"},
    )
    assert response.status_code == 200

    # Sign in with new password
    response = await async_client.post(
        "/api/auth/signin",
        json={"username": "updateduser", "email": "update@example.com", "password": "newpassword"},
    )
    assert response.status_code == 202
    assert "token" in response.json()["authorizedAccount"]
