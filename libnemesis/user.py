
import ldap.filter

import srusers

from team import Team
from college import College
import constants

class User(object):
    @classmethod
    def create_user(cls, username, password=None):
        if User.can_authenticate(username, password):
            return AuthenticatedUser(username, password)
        else:
            return User(username)

    @classmethod
    def email_used(cls, email):
        email = ldap.filter.escape_filter_chars(email)
        userids = srusers.user.search(email = email)
        return len(userids) > 0

    @classmethod
    def name_used(cls, first_name, last_name):
        first_name = ldap.filter.escape_filter_chars(first_name)
        last_name = ldap.filter.escape_filter_chars(last_name)
        userids = srusers.user.search(cname = first_name, sname = last_name)
        return len(userids) > 0

    @classmethod
    def create_new_user(cls, requesting_user, college, first_name, last_name):
        if not requesting_user.can_register_users:
            raise Exception("requesting user '%s' is not permitted to create new users" % (requesting_user.username))

        if not college in requesting_user.colleges:
            raise Exception("requesting user '%s' is not in the requested college '%s'" % (requesting_user.username, college))

        username = srusers.new_username(college, first_name, last_name)
        u = srusers.user(username)
        u.cname = first_name
        u.sname = last_name
        u.email = ''
        u.save()
        return User(username)

    @classmethod
    def can_authenticate(cls, username, password):
        return password is not None and srusers.user(username).bind(password)

    def __init__(self, username):
        self._user = srusers.user(username)
        if not self._user.in_db:
            raise Exception("user '%s' does not exist in database" % (username))

        # cache any groups we change, since searching the database for them
        # after our changes will yield very odd results.
        self._modified_groups = set()

        self._cached_groups = None

    @property
    def _groups(self):
        if self._cached_groups is None:
            self._cached_groups = set(self._user.groups())

        return self._cached_groups

    def set_password(self, password):
        self._user.set_passwd(old=None, new=password)

    def set_email(self, email):
        self._user.email = email

    def set_first_name(self, first_name):
        self._user.cname = first_name

    def set_last_name(self, last_name):
        self._user.sname = last_name

    def _set_group(self, new_group, current_groups):
        """
        Helper method to change ownership from a possible collection of
        groups to a single other group.
        """
        already_member = False
        for gname in current_groups:
            if gname == new_group:
                already_member = True
                continue
            grp = srusers.group(gname)
            if self.username in grp.members:
                grp.user_rm(self.username)
                self._modified_groups.add(grp)

        if not already_member:
            new_grp = srusers.group(new_group)
            new_grp.user_add(self.username)
            self._modified_groups.add(new_grp)

    def set_team(self, new_team):
        current = [t.name for t in self.teams]
        self._set_group(new_team, current)

    def set_college(self, new_college):
        self._set_group(new_college, self.colleges)

    def make_student(self):
        self._set_group(constants.COMPETITORS_GROUP, [constants.TEAM_LEADERS_GROUP])

    def make_teacher(self):
        self._set_group(constants.TEAM_LEADERS_GROUP, [constants.COMPETITORS_GROUP])

    @property
    def username(self):
        return self._user.username

    def is_authenticated(self):
        return False

    @property
    def email(self):
        return self._user.email

    @property
    def first_name(self):
        return self._user.cname

    @property
    def last_name(self):
        return self._user.sname

    def details_dictionary_for(self, other):
        assert other.can_view(self)
        build =  {
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "is_blueshirt": self.is_blueshirt,
            "is_student": self.is_student,
            "is_team_leader": self.is_teacher,
            "has_withdrawn": self.has_withdrawn,
            "has_media_consent": self.has_media_consent,
            "teams": list(self._team_group_names),
            "colleges": list(self._college_group_names),
        }

        if other.is_teacher or self == other:
            build["email"] = self.email

        return build

    @property
    def _team_group_names(self):
        return filter(Team.valid_team_name, self._groups)

    @property
    def teams(self):
        return set(
            Team(g)
            for g in self._team_group_names
        )

    @property
    def _college_group_names(self):
        return filter(College.is_valid_college_name, self._groups)

    @property
    def colleges(self):
        return [
            College(g)
            for g in self._college_group_names
        ]

    @property
    def has_media_consent(self):
        return constants.MEDIA_CONSENT_GRANTED_GROUP in self._groups

    def got_media_consent(self):
        self._set_group(constants.MEDIA_CONSENT_GRANTED_GROUP, [])

    @property
    def has_withdrawn(self):
        return constants.WITHDRAWN_GROUP in self._groups

    def withdraw(self):
        self._set_group(constants.WITHDRAWN_GROUP, [])

    @property
    def is_student(self):
        return constants.COMPETITORS_GROUP in self._groups

    @property
    def is_teacher(self):
        return constants.TEAM_LEADERS_GROUP in self._groups

    @property
    def can_register_users(self):
        return False

    @property
    def is_blueshirt(self):
        return constants.BLUESHIRTS_GROUP in self._groups

    @property
    def is_blueshirt_extra(self):
        return constants.BLUESHIRTS_EXTRA_GROUP in self._groups

    @property
    def can_record_media_consent(self):
        return constants.MEDIA_CONSENT_ADMINS_GROUP in self._groups

    def can_administrate(self, other_user_or_username):
        #if it's a string return the internal comparison with a user object
        if isinstance(other_user_or_username, basestring):
            other_user_or_username = User(other_user_or_username)

        return self._can_administrate(other_user_or_username)

    def can_view(self, user):
        return False

    def can_withdraw(self, user):
        return False

    def manages_team(self, team_or_team_name):
        # if it's a string get an internal representation
        if isinstance(team_or_team_name, basestring):
            if not Team.valid_team_name(team_or_team_name):
                # raise?
                return False
            else:
                team_or_team_name = Team(team_or_team_name)

        return self._manages_team(team_or_team_name)

    def _can_administrate(self, user_object):
        return False

    def _manages_team(self, team_object):
        return False

    def __eq__(self, other):
        if isinstance(other, User):
            return self.username == other.username
        else:
            return False

    def __hash__(self):
        return self.username.__hash__()

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        type_ = self.__class__.__name__
        return "{0}({1})".format(type_, self.username)

    def save(self):
        self._cached_groups = None
        self._user.save()
        for g in self._modified_groups:
            g.save()

    def delete(self):
        for gid in self._user.groups():
            g = srusers.group(gid)
            g.user_rm(self.username)
            g.save()
        self._user.delete()

class AuthenticatedUser(User):
    def __init__(self, username, password):
        # check their password
        user = srusers.user(username)
        assert user.bind(password)

        # Call parent init, which will, among other things, ensure that the
        # LDAP binding goes back to being via the manager credential, not the
        # one we just checked above.
        super(AuthenticatedUser, self).__init__(username)

        self._viewable_users_cache = set()

    @property
    def can_register_users(self):
        return self.is_teacher or self.is_blueshirt

    def _any_college_has_member(self, user_object):
        return user_object in self._viewable_users

    def _manages_team(self, team_object):
        return self.is_teacher and team_object in self.teams

    @property
    def _viewable_users(self):
        if not self._viewable_users_cache:
            self._viewable_users_cache.update(
                user
                for college in self.colleges
                for user in college.users
            )

        return self._viewable_users_cache

    def _can_administrate(self, user_object):
        return user_object == self or (
            (self.is_teacher or self.is_blueshirt) and
            self._any_college_has_member(user_object) and
            not user_object.is_blueshirt
        )

    def is_authenticated(self):
        return True

    def can_view(self, user):
        return self.can_administrate(user) or self.is_blueshirt_extra \
            or self.can_record_media_consent


    def can_withdraw(self, user):
        return not user.is_blueshirt and self.is_teacher and self != user

class NullUser:
    def __init__(self):
        self.can_register_users = False
        self.username = ""
        self.is_blueshirt = False

    def can_administrate(self, other_user):
        return False

    def can_view(self, user):
        return False

    def can_withdraw(self, user):
        return False

    def is_authenticated(self):
        return False

    @property
    def colleges(self):
        return []
