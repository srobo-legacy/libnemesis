import srusers
import json
from user import AuthenticatedUser, NullUser

class AuthHelper:
    def __init__(self, req):
        if req.authorization:
            form = {"username":req.authorization.username,
                    "password":req.authorization.password}
        else:
            form = {}
        self.form = form
        self._auth_succeeded = None

    @property
    def request_has_username(self):
        return self.form.has_key("username")

    @property
    def request_has_password(self):
        return self.form.has_key("password")

    @property
    def user_exists(self):
        return self.request_has_username and srusers.user.exists(self.form["username"])

    @property
    def password_correct(self):
        return self.request_has_password and srusers.user(self.form["username"]).bind(self.form["password"])

    @property
    def auth_will_succeed(self):
        if self._auth_succeeded is None:
            self._auth_succeeded = self.user_exists and self.password_correct
        return self._auth_succeeded

    @property
    def user(self):
        if self.auth_will_succeed:
            return AuthenticatedUser(self.form["username"], self.form["password"])
        else:
            return NullUser()

    @property
    def auth_error_json(self):
        auth_errors = []
        if not self.request_has_username:
            auth_errors.append("NO_USERNAME")
        if not self.request_has_password:
            auth_errors.append("NO_PASSWORD")

        if not self.user_exists:
            auth_errors.append("WRONG_PASSWORD")
        elif not self.password_correct:
            auth_errors.append("WRONG_PASSWORD")
        return json.dumps({"authentication_errors":auth_errors})
