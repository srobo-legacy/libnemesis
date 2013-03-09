import srusers
import re

import user

class College:
    @classmethod
    def is_valid_college_name(cls, string):
        return re.match("college.*", string) is not None

    def __init__(self, group_name):
        self._group = srusers.group(group_name)
        self._group_name = group_name

    @property
    def name(self):
        return self._group.desc

    @property
    def teams(self):
        teams = set()
        for user_object in self.users:
            teams.update(user_object.teams)

        return teams

    @property
    def users(self):
        return [user.User.create_user(username=un) for un in self._group.members]

    def __eq__(self, other):
        print "called"
        if isinstance(other, College):
            return self._group_name == other._group_name
        elif isinstance(other, basestring):
            return self._group_name == other
        else:
            return False

    def __neq__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self._group_name)

    def __unicode__(self):
        return self._group_name

    def __str__(self):
        return self._group_name
