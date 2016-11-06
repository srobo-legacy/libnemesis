import re
import srusers

import user

class Team:
    """A lazy wrapper around an LDAP group representing a team."""

    @classmethod
    def valid_team_name(cls, team_name):
        return re.match("^team-[0-9A-Z]+$", team_name) != None

    def __init__(self, name):
        self._name = name
        self._cached_group = None

    @property
    def name(self):
        return self._name

    @property
    def _group(self):
        if self._cached_group is None:
            self._cached_group = srusers.group(self._name)

        return self._cached_group

    @property
    def users(self):
        return [user.User(un) for un in self._group.members]

    def __eq__(self, other):
        return isinstance(other, Team) and other.name == self.name

    def __neq__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.name)
