from fastapi import Depends, HTTPException, status, Request

from src.entity.models import User, Role
from src.services.auth import auth_service


class RoleAccess:
    def __init__(self, allowed_roles: list[Role]):
        """
        :param allowed_roles: list[Role]: Specify which roles are allowed to access this route
        """
        self.allowed_roles = allowed_roles

    async def __call__(self, request: Request, user: User = Depends(auth_service.get_current_user)):
        """
        :param request: Request: Get the request object from the FastAPI application
        :param user: User: Get the current user object from the request dependency
        :return: The current user object if the user is in the allowed roles list or raise an HTTPException with status code 403 and detail "FORBIDDEN" if the user is not in the allowed roles list
        """
        print(user.role, self.allowed_roles)
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="FORBIDDEN")
