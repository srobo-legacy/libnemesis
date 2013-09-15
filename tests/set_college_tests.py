
from nose.tools import with_setup

from libnemesis import *

ORIG_COLLEGE_NAME = 'college-STA'
NEW_COLLEGE_NAME = 'college-STB'

def setUp():
    # Create a temp user & colleges
    sru = srusers.user('st_user1')
    sru.email = 'st_user1@nowhere.net'
    sru.cname = 'steve'
    sru.sname = 'user1'
    sru.save()
    other_group = srusers.group('st_other_group')
    other_group.user_add(sru)
    other_group.save()
    orig_college = srusers.group(ORIG_COLLEGE_NAME)
    orig_college.user_add(sru)
    orig_college.save()
    new_college = srusers.group(NEW_COLLEGE_NAME)
    new_college.save()

def tearDown():
    # Remove the temp user & colleges
    def del_if_in_db(groupname):
        grp = srusers.group(groupname)
        if grp.in_db:
            grp.rm()
    del_if_in_db('st_other_group')
    del_if_in_db(ORIG_COLLEGE_NAME)
    del_if_in_db(NEW_COLLEGE_NAME)
    sru = srusers.user('st_user1')
    if sru.in_db:
        sru.delete()

@with_setup(setUp, tearDown)
def test_college_set_in_user():
    u = User.create_user('st_user1')

    u.set_college(NEW_COLLEGE_NAME)
    u.save()

    u_colleges = u.colleges
    assert set(u_colleges) == set([NEW_COLLEGE_NAME])

@with_setup(setUp, tearDown)
def test_college_set_in_db():
    u = User.create_user('st_user1')

    u.set_college(NEW_COLLEGE_NAME)
    u.save()

    sru = srusers.user('st_user1')
    sru_groups = sru.groups()
    assert set(sru_groups) == set([NEW_COLLEGE_NAME, 'st_other_group'])
