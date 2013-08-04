import srusers
from team import *
from college import *

class User(object):
    @classmethod
    def create_user(cls, username, password=None):
        if User.can_authenticate(username, password):
            return AuthenticatedUser(username, password)
        else:
            return User(username)

    @classmethod
    def can_authenticate(cls, username, password):
        return password is not None and srusers.user(username).bind(password)

    def __init__(self, username):
        self._user = srusers.user(username)
        if not self._user.in_db:
            raise Exception("user does not exist in database")

        # cache any groups we change, since searching the database for them
        # after our changes will yield very odd results.
        self._modified_groups = set()

    def set_password(self, password):
        self._user.set_passwd(old=None, new=password)

    def set_email(self, email):
        self._user.email = str(email)

    def set_first_name(self, first_name):
        self._user.cname = str(first_name)

    def set_last_name(self, last_name):
        self._user.sname = str(last_name)

    def set_team(self, new_team):
        already_member = False
        for t in self.teams:
            if t.name == new_team:
                already_member = True
                continue
            grp = srusers.group(t.name)
            if self.username in grp.members:
                grp.user_rm(self.username)
                self._modified_groups.add(grp)

        if not already_member:
            new_grp = srusers.group(new_team)
            new_grp.user_add(self.username)
            self._modified_groups.add(new_grp)

    @property
    def username(self):
        return self._user.username

    def is_authenticated(self):
        return False

    @property
    def email(self):
        return self._user.email

    def details_dictionary_for(self, other):
        assert other.can_administrate(self)
        build =  {
                "username":self.username,
                "first_name":self._user.cname,
                "last_name":self._user.sname,
                "teams":[x.name for x in self.teams],
                "colleges":[x.group_name for x in self.colleges]
                }

        if other.is_teacher or self == other:
            build["email"] = self.email

        return build

    @property
    def teams(self):
        teams = set()
        teams.update(self._valid_team_groups())
        return teams

    @property
    def colleges(self):
        return [College(g) for g in self._user.groups()\
                if College.is_valid_college_name(g)]


    @property
    def is_teacher(self):
        return "teachers" in self._user.groups()

    def can_register_users(self):
        return False

    @property
    def is_blueshirt(self):
        return "mentors" in self._user.groups()

    def can_administrate(self, other_user_or_username):
        #if it's a string return the internal comparison with a user object
        if isinstance(other_user_or_username, basestring):
            other_user_or_username = User(other_user_or_username)

        return self._can_administrate(other_user_or_username)

    def manages_team(self, team_or_team_name):
        # if it's a string get an internal representation
        if isinstance(team_or_team_name, basestring):
            if not Team.valid_team_name(team_or_team_name):
                # raise?
                return False
            else:
                team_or_team_name = Team(team_or_team_name)

        return self._manages_team(team_or_team_name)

    def _valid_team_groups(self):
        return [Team(g) for g in self._user.groups() if Team.valid_team_name(g)]

    def _can_administrate(self, user_object):
        return False

    def _manages_team(self, team_object):
        return False

    def __eq__(self, other):
        if isinstance(other, User) or isinstance(other, AuthenticatedUser):
            return self._user.username == other._user.username
        else:
            return False

    def __hash__(self):
        return self._user.username.__hash__()

    def __ne__(self, other):
        return not self.__eq__(other)

    def save(self):
        self._user.save()
        for g in self._modified_groups:
            g.save()

class AuthenticatedUser(User):
    def __init__(self, username, password):
        # check their password
        user = srusers.user(username)
        assert user.bind(password)

        # Call parent init, which will, among other things, ensure that the
        # LDAP binding goes back to being via the manager credential, not the
        # one we just checked above.
        super(AuthenticatedUser, self).__init__(username)

        self._password = password
        self._viewable_users = set()

    def can_register_users(self):
        return self.is_teacher or self.is_blueshirt

    def _can_administrate(self, user_object):
        return self._can_view_if_teacher_or_blueshirt(user_object) or\
               user_object == self

    def _any_college_has_member(self, user_object):
        self._setup_viewable_users()

        return user_object in self._viewable_users

    def _any_team_has_member(self, user_object):
        for team in self.teams:
            for user in team.users:
                if user == user_object:
                    return True
        return False

    def _manages_team(self, team_object):
        return self.is_teacher and team_object in self.teams

    def _setup_viewable_users(self):
        if len(self._viewable_users) == 0:
            for college in self.colleges:
                for user in college.users:
                    self._viewable_users.add(user)

    def _can_view_if_teacher_or_blueshirt(self, user_object):
        return (self.is_teacher or self.is_blueshirt) and \
               self._any_college_has_member(user_object) and \
               not user_object.is_blueshirt

    def is_authenticated(self):
        return True

class NullUser:
    def __init__(self):
        self.can_register_users = False
        self.username = ""
        self.is_blueshirt = False

    def can_administrate(self, other_user):
       return False

    def is_authenticated(self):
        return False

    @property
    def colleges(self):
        return []
