from fastapi import APIRouter, Depends, HTTPException, status, Security, \
    BackgroundTasks, Request, Response
from fastapi.security import OAuth2PasswordRequestForm, \
    HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.repository import users as repository_users
from src.schemas.user import UserResponse, TokenSchema, UserSchema, RequestEmail
from src.services.auth import auth_service
from src.services.email import send_email
from src.conf import messages

router = APIRouter(prefix="/auth", tags=["auth"])
get_refresh_token = HTTPBearer()


@router.post("/signup", response_model=UserResponse,
             status_code=status.HTTP_201_CREATED)
async def signup(body: UserSchema, bt: BackgroundTasks, request: Request,
                 db: AsyncSession = Depends(get_db)):
    """
    The signup function creates a new user in the database.
    :param body: UserSchema: Get the data from the request body and create a new user in the database with it
    :param bt: BackgroundTasks: Add a task to the background tasks to send an email to the user when they sign up
    :param request: Request: Get the base url of the application
    :param db: AsyncSession: Create a database session for the user to be created in the database
    :return: A user object with the new data from the request body
    """
    try:
        exist_user = await repository_users.get_user_by_email(body.email, db)
        if exist_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=messages.ACCOUNT_EXIST)
        body.password = auth_service.get_password_hash(body.password)
        new_user = await repository_users.create_user(body, db)
        bt.add_task(send_email, new_user.email, new_user.username,
                    str(request.base_url))
        return new_user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=str(e))


@router.post("/login", response_model=TokenSchema)
async def login(body: OAuth2PasswordRequestForm = Depends(),
                db: AsyncSession = Depends(get_db)):
    """
    The login function creates a new access token for a user.
    :param body: OAuth2PasswordRequestForm: Get the username and password from the request body
    :param db: AsyncSession: Create a database session for the user to be logged in to the database
    :return: A token object with an access token and refresh token for the user to be logged in to the application
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=messages.EMAIL_NOT_FOUND)
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=messages.EMAIL_NOT_CONFIRMED)
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=messages.INCORRECT_PASSWORD)
    access_token = await auth_service.create_access_token(
        data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(
        data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token,
            "token_type": "bearer"}


@router.get("/refresh_token", response_model=TokenSchema)
async def refresh_token(
        credentials: HTTPAuthorizationCredentials = Security(get_refresh_token),
        db: AsyncSession = Depends(get_db)):
    """
    The refresh_token function is used to refresh the access token.
    :param credentials: HTTPAuthorizationCredentials: Get the refresh token from the request body
    :param db: AsyncSession: Pass the database session to the function
    :return: A token object with an access token and refresh token for the user to be logged in to the application
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=messages.INVALID_REFRESH_TOKEN)
    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token,
            "token_type": "bearer"}


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    The confirmed_email function is used to confirm a user's email address.
    :param token: str: Pass the token to the function
    :param db: AsyncSession: Pass the database session to the function
    :return: A message confirming the email has been confirmed or an error message if the token is invalid or expired
    """
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=messages.USER_NOT_FOUND)
    if user.confirmed:
        return {"message": "Verification has already been passed"}
    await repository_users.confirmed_email(email, db)
    return {"message": "Verification successful"}


@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks,
                        request: Request,
                        db: AsyncSession = Depends(get_db)):
    """
    The request_email function sends an email to the user with a confirmation link.
    :param body: RequestEmail: Get the email from the request body
    :param background_tasks: BackgroundTasks: Send the email in the background
    :param request: Request: Get the base url of the application
    :param db: AsyncSession: Create a database session for the user to be logged in to the database
    :return: A message confirming that the email has been sent
    """
    user = await repository_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username,
                                  str(request.base_url))
    return {"message": "Check your email for confirmation."}


@router.get("/{username}")
async def request_email(username: str, response: Response,
                        db: AsyncSession = Depends(get_db)):
    """
    The request_email function sends an email to the user with a confirmation link.
    :param username: str: Get the username from the URL
    :param response: Response: Get the response object
    :param db: AsyncSession: Pass the database session to the function
    :return: A message confirming that the email has been sent
    """
    print("-------------------------------------------------")
    print(f"{username} Save that the user open email in DB")
    print("-------------------------------------------------")
    return FileResponse("src/static/open_check.png", media_type="image/png",
                        content_disposition_type="inline")
