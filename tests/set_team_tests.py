
from nose.tools import with_setup

from libnemesis import *

ORIG_TEAM_NAME = 'team-STA'
NEW_TEAM_NAME = 'team-STB'

def setUp():
    # Create a temp user & teams
    sru = srusers.user('st_user1')
    sru.email = 'st_user1@nowhere.net'
    sru.cname = 'steve'
    sru.sname = 'user1'
    sru.save()
    other_group = srusers.group('st_other_group')
    other_group.user_add(sru)
    other_group.save()
    orig_team = srusers.group(ORIG_TEAM_NAME)
    orig_team.user_add(sru)
    orig_team.save()
    new_team = srusers.group(NEW_TEAM_NAME)
    new_team.save()

def tearDown():
    # Remove the temp user & teams
    def del_if_in_db(groupname):
        grp = srusers.group(groupname)
        if grp.in_db:
            grp.rm()
    del_if_in_db('st_other_group')
    del_if_in_db(ORIG_TEAM_NAME)
    del_if_in_db(NEW_TEAM_NAME)
    sru = srusers.user('st_user1')
    if sru.in_db:
        sru.delete()

@with_setup(setUp, tearDown)
def test_team_set_in_user():
    u = User.create_user('st_user1')

    u.set_team(NEW_TEAM_NAME)
    u.save()

    u_teams = [t.name for t in u.teams]
    assert set(u_teams) == set([NEW_TEAM_NAME])

@with_setup(setUp, tearDown)
def test_team_set_in_db():
    u = User.create_user('st_user1')

    u.set_team(NEW_TEAM_NAME)
    u.save()

    sru = srusers.user('st_user1')
    sru_groups = sru.groups()
    assert set(sru_groups) == set([NEW_TEAM_NAME, 'st_other_group'])
