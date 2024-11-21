from auth import utils as auth_utils
from users.schemas import UserSchema

john = UserSchema(
    username="John",
    password=auth_utils.hash_password("qwerty"),
    email="jhon@example.com",
)
sam = UserSchema(
    username="Sam",
    password=auth_utils.hash_password("secret"),
)
user_db: dict[str, UserSchema] = {
    john.username: john,
    sam.username: sam,
}
