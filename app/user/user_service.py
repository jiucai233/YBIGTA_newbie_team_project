from app.user.user_repository import UserRepository
from app.user.user_schema import User, UserLogin, UserUpdate

class UserService:
    def __init__(self, userRepoitory: UserRepository) -> None:
        self.repo = userRepoitory

    def login(self, user_login: UserLogin) -> User:
        '''
        Login user with email and password
        compare with stored user data in the repository
        if the data cannot match, raise an ValueError
        '''
        user_email = user_login.email
        user_password = user_login.password
        user = self.repo.get_user_by_email(user_email)
        if not user:
            raise ValueError("User not Found.")
        if user.password != user_password:
            raise ValueError("Invalid ID/PW")
        return user
        
    def register_user(self, new_user: User) -> User:
        '''
        Register a new user, if the email already exists, raise an ValueError
        Otherwise, save the new user to the repository
        '''
        new_user_email = new_user.email
        existing = self.repo.get_user_by_email(new_user_email)
        if existing:
            raise ValueError("User already Exists.")

        self.repo.save_user(new_user)
   
        return new_user

    def delete_user(self, email: str) -> User:
        '''
        Delete a user by email, if the email does not exist, raise an ValueError
        Otherwise, delete the user from the repository
        '''
        existing = self.repo.get_user_by_email(email)
        if not existing:
            raise ValueError("User not Found.")

        deleted_user = self.repo.delete_user(existing)
        return deleted_user

    def update_user_pwd(self, user_update: UserUpdate) -> User:
        '''
        Update a user's password, if the email does not exist, raise an ValueError
        Otherwise, update the user's password in the repository
        '''
        # get var
        user_email = user_update.email
        new_password = user_update.new_password

        # query
        user_in_db = self.repo.get_user_by_email(user_email)
        if not user_in_db:
            raise ValueError("User not Found.")

        # update
        user_in_db.password = new_password
        updated_user = self.repo.save_user(user_in_db)
        return updated_user
        