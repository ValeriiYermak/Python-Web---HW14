import redis
import pickle

from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from src.database.db import get_db
from src.repository import users as repository_users
from src.conf.config import config


class Auth:
    """
    Class for working with JWT tokens and hashing passwords in the application and database for authentication.

    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = config.SECRET_KEY_JWT
    ALGORITHM = config.ALGORITHM
    cache = redis.Redis(
        host=config.REDIS_DOMAIN,
        port=config.REDIS_PORT,
        db=0,
        password=config.REDIS_PASSWORD,
    )

    def verify_password(self, plain_password, hashed_password):
        """
        The verify_password function takes in a plain text password and hashed password, and returns True if the
        password is correct and False if it is not.
        :param plain_password: str: Pass in the plain text password that the user enters in the password field in the
        :param hashed_password: str: Pass in the hashed password from the database
        :return: A boolean
        """
        print(plain_password, hashed_password)
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        The get_password_hash function takes a password as input and returns the password hash.
        :param password: str: Get the password from the user input field in the frontend application
        :return: The password hash of the password that was passed in the function call
        """
        return self.pwd_context.hash(password)

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

    async def create_access_token(self, data: dict,
                                  expires_delta: Optional[float] = None):
        """
        The create_access_token function creates an access token for a user. The access token is valid for 15 minutes.
        :param data: dict: Pass the data that you want to encode in the token
        :param expires_delta: Optional[float]: Set the expiration time for the token
        :return: A string which is the access token for the user to be able to access the application with their credentials
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update(
            {"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY,
                                          algorithm=self.ALGORITHM)
        return encoded_access_token

    async def create_refresh_token(self, data: dict,
                                   expires_delta: Optional[float] = None):
        """
        The create_refresh_token function creates a refresh token for a user. The refresh token is valid for 7 days.
        :param data: dict: Pass the data that you want to encode in the token
        :param expires_delta: Optional[float]: Set the expiration time for the token
        :return: A string which is the refresh token for the user to be able to get a new access token when it expires in 7 days or less
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update(
            {"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY,
                                           algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        """
        The decode_refresh_token function takes a refresh token as input and returns the email associated with it.
        :param refresh_token: str: Specify the type of the argument here
        :return: A string which is the email address of the user who is trying to refresh their access token
        """
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY,
                                 algorithms=[self.ALGORITHM])
            if payload['score'] == "refresh_token":
                email = payload["sub"]
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid scope for requested token")
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could not validate credentials")

    async def get_current_user(self, token: str = Depends(oauth2_scheme),
                               db: AsyncSession = Depends(get_db)):
        """
        The get_current_user function takes a token and returns the user associated with that token.
        :param token: str: Get the token from the request headers
        :param db: AsyncSession: Pass the database session to the repository functions
        :return: A dictionary with the user's email and scope access or raise an exception if the token is invalid or expired
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, self.SECRET_KEY,
                                 algorithms=[self.ALGORITHM])
            if payload['scope'] == "access_token":
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user_hash = str(email)

        user = self.cache.get(user_hash)

        if user is None:
            print("User from database")
            user = await repository_users.get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            self.cache.set(user_hash, pickle.dumps(user))
            self.cache.expire(user_hash, 300)
        else:
            print("User from cache")
            user = pickle.loads(user)
        return user

    def create_email_token(self, data: dict):
        """
        The create_email_token function takes in a dictionary of data and returns a token.
        :param data: dict: Pass in the data that you want to encode in the token
        :return: A token string which is valid for 15 minutes from the time it is created
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=1)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def get_email_from_token(self, token: str):
        """
        The get_email_from_token function takes a token as input and returns the email address associated with that token.
        :param token: str: Get the token from the request body
        :return: A string which is the email address of the user who is trying to reset their password
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY,
                                 algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could not validate credentials")


auth_service = Auth()
