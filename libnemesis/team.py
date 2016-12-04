import re

import lazy_group

class Team(lazy_group.LazyGroup):
    """A lazy wrapper around an LDAP group representing a team."""

    @classmethod
    def valid_team_name(cls, team_name):
        return re.match("^team-[0-9A-Z]+$", team_name) != None

    @property
    def name(self):
        return self.group_name

    def __eq__(self, other):
        return isinstance(other, Team) and other.name == self.name

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.name)
