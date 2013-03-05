import srusers
import re

class College:
    @classmethod
    def is_valid_college_name(cls, string):
        return re.match("college.*", string) is not None

    def __init__(self, group_name):
        self._group = srusers.group(group_name)

    @property
    def name(self):
        return self._group.desc

    @property
    def teams(self):
        teams = set()
        for user in self.users:
            teams.update(user.teams)

        return teams

    @property
    def users(self):
        return [User.create_user(username=un) for un in self._group.members]
