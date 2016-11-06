import srusers

import lazy_group

class College(lazy_group.LazyGroup):
    """A lazy wrapper around an LDAP group representing a college."""

    @classmethod
    def all_college_names(cls):
        all_groups = srusers.groups.list()
        return [g for g in all_groups if College.is_valid_college_name(g)]

    @classmethod
    def is_valid_college_name(cls, string):
        return string.startswith(srusers.constants.COLLEGE_PREFIX)

    @property
    def name(self):
        return self._group.desc

    @property
    def teams(self):
        teams = set()
        for user_object in self.users:
            # Only allow teams which team-leaders or students are members
            # of to count. Blueshirts are likely to be added to many teams
            # and colleges but we don't want that to affect the teams
            # which are actually related to the colleges.
            if user_object.is_teacher or user_object.is_student:
                teams.update(user_object.teams)

        return teams

    def _get_counts(self):
        counts = {
            "team_leaders": 0,
            "students": 0,
            "media_consent": 0,
            "withdrawn": 0,
        }

        for user in self.users:
            if user.is_blueshirt:
                continue
            if user.is_teacher:
                counts["team_leaders"] += 1
            if user.is_student:
                counts["students"] += 1
            if user.has_media_consent:
                counts["media_consent"] += 1
            if user.has_withdrawn:
                counts["withdrawn"] += 1

        return counts

    def details_dictionary_for(self, requesting_user):
        user_in_college = self in requesting_user.colleges
        assert user_in_college or requesting_user.is_blueshirt

        build = {
            "name": self.name,
            "teams": [t.name for t in self.teams],
            "counts": self._get_counts(),
        }

        if user_in_college:
            build["users"] = [
                u.username
                for u in self.users
                if requesting_user.can_administrate(u)
            ]

        return build


    def __eq__(self, other):
        if isinstance(other, College):
            return self.group_name == other.group_name
        elif isinstance(other, basestring):
            return self.group_name == other
        else:
            return False

    def __neq__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.group_name)

    def __unicode__(self):
        return self.group_name

    def __str__(self):
        return self.group_name
