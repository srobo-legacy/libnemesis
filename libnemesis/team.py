import re
import srusers

import user

class Team:
    @classmethod
    def valid_team_name(cls, team_name):
        return re.match("^team-[0-9A-Z]+$", team_name) != None

    def __init__(self, name):
        self._group = srusers.group(name)
        self.name = name

    @property
    def users(self):
        return [user.User(un) for un in self._group.members]
