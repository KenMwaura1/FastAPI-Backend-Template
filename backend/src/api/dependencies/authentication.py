
import fastapi
from fastapi.security import HTTPBearer
from src.config.manager import settings
from src.api.dependencies.repository import get_repository
from src.repository.crud.account import AccountCRUDRepository
from src.securities.authorizations.jwt import jwt_generator
from src.utilities.exceptions.http.exc_401 import http_exc_401_unauthorized_request
from src.models.db.account import Account
from src.utilities.exceptions.database import EntityDoesNotExist

reusable_oauth2 = HTTPBearer(
    scheme_name="Authorization"
)

async def get_current_account(
    token: str = fastapi.Depends(reusable_oauth2),
    account_repo: AccountCRUDRepository = fastapi.Depends(get_repository(repo_type=AccountCRUDRepository)),
) -> Account:
    try:
        user_id = jwt_generator.retrieve_details_from_token(token=token.credentials, secret_key=settings.JWT_SECRET_KEY)
    except ValueError:
        raise await http_exc_401_unauthorized_request()

    try:
        db_account = await account_repo.read_account_by_id(id=int(user_id))
    except EntityDoesNotExist:
        raise await http_exc_401_unauthorized_request()
    return db_account
