
from nose.tools import raises, with_setup

from libnemesis import *

def remove_user(name):
    def helper():
        u = srusers.user(name)
        if u.in_db:
            for gid in u.groups():
                g = srusers.group(gid)
                g.user_rm(name)
                g.save()
            u.delete()

    return helper

def test_can_make_user():
    User.create_user("teacher_coll1")

def test_nonexistant_user_raises():
    try:
        User.create_user("qowiejfqwoi")
        assert False
    except:
        pass

def check_new_user(u):
    assert u.username == '1_fl1'
    assert u.first_name == 'first'
    assert u.last_name == 'last'
    assert u.email == ''
    assert not u.is_blueshirt
    assert not u.is_student
    assert not u.is_teacher
    colleges = set(u.colleges)
    assert colleges == set()
    teams = set(u.teams)
    assert teams == set()

def test_email_used():
    used = User.email_used('student1@example.com')
    assert used

def test_email_not_used():
    used = User.email_used('nope@srobo.org')
    assert used == False

def test_wildcard_email_not_used():
    used = User.email_used('*')
    assert used == False

def test_name_used():
    used = User.name_used('student1', 'student')
    assert used

def test_name_not_used():
    used = User.name_used('John', 'Smith')
    assert used == False

def test_wildcard_name_not_used():
    used = User.name_used('student*', 'student')
    assert used == False

@with_setup(remove_user('to-withdraw'), remove_user('to-withdraw'))
def test_withdrawal():
    username = 'to-withdraw'
    sru = srusers.user(username)
    sru.cname = 'to'
    sru.sname = 'withdraw'
    sru.email = ''
    sru.save()

    u = User.create_user(username)
    assert not u.has_withdrawn
    u.withdraw()
    u.save()
    assert u.has_withdrawn

def test_withdrawn_false_1():
    u = User.create_user("student_coll1_1")
    assert not u.has_withdrawn

def test_withdrawn_false_2():
    u = User.create_user("student_coll1_1", "cows")
    data = u.details_dictionary_for(u)
    assert not data['has_withdrawn']

def create_withdrawn(username):
    sru = srusers.user(username)
    sru.cname = 'to'
    sru.sname = 'withdraw'
    sru.email = ''
    sru.save()
    g = srusers.group('withdrawn')
    g.user_add(sru)
    g.save()
    return sru

@with_setup(remove_user('to-withdraw'), remove_user('to-withdraw'))
def test_withdrawn_true_1():
    username = 'to-withdraw'
    create_withdrawn(username)

    u = User.create_user(username)
    assert u.has_withdrawn

@with_setup(remove_user('to-withdraw'), remove_user('to-withdraw'))
def test_withdrawn_true_2():
    username = 'to-withdraw'
    sru = create_withdrawn(username)
    password = 'bees'
    sru.set_passwd(new = password)

    u = User.create_user(username, password)
    data = u.details_dictionary_for(u)
    assert data['has_withdrawn']

def test_media_consent_false_1():
    u = User.create_user("student_coll1_1")
    assert not u.has_media_consent

def test_media_consent_false_2():
    u = User.create_user("student_coll1_1", "cows")
    data = u.details_dictionary_for(u)
    assert not data['has_media_consent']

def create_media_consent(username):
    sru = srusers.user(username)
    sru.cname = 'to'
    sru.sname = 'consent'
    sru.email = ''
    sru.save()
    g = srusers.group('media-consent')
    g.user_add(sru)
    g.save()
    return sru

@with_setup(remove_user('to-consent'), remove_user('to-consent'))
def test_media_consent_true_1():
    username = 'to-consent'
    create_media_consent(username)

    u = User.create_user(username)
    assert u.has_media_consent

@with_setup(remove_user('to-consent'), remove_user('to-consent'))
def test_media_consent_true_2():
    username = 'to-consent'
    sru = create_media_consent(username)
    password = 'bees'
    sru.set_passwd(new = password)

    u = User.create_user(username, password)
    data = u.details_dictionary_for(u)
    assert data['has_media_consent']

@with_setup(remove_user('to-be-deleted'), remove_user('to-be-deleted'))
def test_delete_user():
    username = 'to-be-deleted'
    sru = srusers.user(username)
    sru.cname = 'to-be'
    sru.sname = 'deleted'
    sru.email = ''
    sru.save()
    for gid in ['students', 'team-ABC', 'college-1']:
        g = srusers.group(gid)
        g.user_add(sru)
        g.save()

    u = User(username)
    u.delete()

    sru = srusers.user(username)
    assert not sru.in_db

    for gid in ['students', 'team-ABC', 'college-1']:
        g = srusers.group(gid)
        assert not username in g.members

@with_setup(remove_user('1_fl1'), remove_user('1_fl1'))
def test_new_user():
    ru = User.create_user("teacher_coll1", "facebees")
    u = User.create_new_user(ru, 'college-1', 'first', 'last')
    check_new_user(u)

@with_setup(remove_user('1_fl1'), remove_user('1_fl1'))
def test_new_user_unicode():
    ru = User.create_user("teacher_coll1", "facebees")
    u = User.create_new_user(ru, u'college-1', u'first', u'last')
    check_new_user(u)

@with_setup(remove_user('1_fl1'), remove_user('1_fl1'))
def test_new_user_made():
    ru = User.create_user("teacher_coll1", "facebees")
    u = User.create_new_user(ru, 'college-1', 'first', 'last')
    u = User.create_user(u.username)
    check_new_user(u)

@with_setup(remove_user('1_fl1'), remove_user('1_fl1'))
def test_new_user_not_authed():
    try:
        ru = User.create_user("teacher_coll1")
        User.create_new_user(ru, 'college-1', 'first', 'last')
        assert False
    except Exception as e:
        assert "teacher_coll1" in e.message

@with_setup(remove_user('1_fl1'), remove_user('1_fl1'))
def test_new_user_not_allowed():
    try:
        ru = User.create_user("student_coll1_1", "cows")
        User.create_new_user(ru, 'college-1', 'first', 'last')
        assert False
    except Exception as e:
        assert "student_coll1_1" in e.message

@with_setup(remove_user('2_fl1'), remove_user('2_fl1'))
def test_new_user_wrong_college():
    try:
        ru = User.create_user("teacher_coll1", "facebees")
        User.create_new_user(ru, 'college-2', 'first', 'last')
        assert False
    except Exception as e:
        assert "teacher_coll1" in e.message
        assert 'college-2' in e.message

def test_user_teams():
    team_names = [team.name for team in User.create_user("student_coll1_1").teams]
    assert team_names == ["team-ABC"]

def test_user_colleges():
    college_names = [college.name for college in User.create_user("student_coll1_1").colleges]
    assert college_names == ["college the first"]

def test_user_colleges2():
    college_names = [college.name for college in User.create_user("teacher_coll2").colleges]
    assert college_names == ["secondary college"]

def test_authed_user_colleges():
    college_names = [college.name for college in User.create_user("teacher_coll1", "facebees").colleges]
    assert college_names == ["college the first"]

def test_is_teacher_1():
    assert not User.create_user("student_coll2_1").is_teacher

def test_is_teacher_2():
    assert User.create_user("teacher_coll1").is_teacher

def test_is_teacher_3():
    assert not User.create_user("blueshirt").is_teacher

def test_is_student_1():
    assert User.create_user("student_coll2_1").is_student

def test_is_student_2():
    assert not User.create_user("teacher_coll1").is_student

def test_is_student_3():
    assert not User.create_user("blueshirt").is_student

def test_is_blueshirt_1():
    assert not User.create_user("student_coll2_1").is_blueshirt

def test_is_blueshirt_2():
    assert not User.create_user("teacher_coll1").is_blueshirt

def test_is_blueshirt_3():
    assert User.create_user("blueshirt").is_blueshirt

def test_can_null_user_register_users():
    nu = NullUser()
    assert not nu.can_register_users

def test_can_plain_student_user_register_users():
    u = User.create_user('student_coll1_1')
    assert not u.can_register_users

def test_can_plain_teacher_user_register_users():
    u = User.create_user('teacher_coll1')
    assert not u.can_register_users

def test_can_plain_blueshirt_user_register_users():
    u = User.create_user('blueshirt')
    assert not u.can_register_users

def test_can_authed_student_user_register_users():
    u = User.create_user('student_coll1_1', 'cows')
    assert not u.can_register_users

def test_can_authed_teacher_user_register_users():
    u = User.create_user('teacher_coll1', 'facebees')
    assert u.can_register_users == True

def test_can_authed_blueshirt_user_register_users():
    u = User.create_user('blueshirt', 'blueshirt')
    assert u.can_register_users == True

def test_user_equality():
    a = User.create_user("teacher_coll1")
    b = User.create_user("teacher_coll1")
    assert a == b

def test_user_nequality():
    a = User.create_user("teacher_coll1")
    b = User.create_user("teacher_coll2")
    assert a != b

def test_authed_user_equality():
    a = User.create_user("teacher_coll1", "facebees")
    b = User.create_user("teacher_coll1")
    assert a == b

def test_authed_user_nequality():
    a = User.create_user("teacher_coll1", "facebees")
    b = User.create_user("teacher_coll2")
    assert a != b

def test_unauthed_cant_see_any():
    a = User.create_user("teacher_coll1")
    users = ["teacher_coll1", "student_coll1_1", "student_coll1_2"]
    results = [a.can_administrate(user) for user in users]
    assert not any(results)

def test_authed_can_see_self():
    user_passwords = [("teacher_coll1", "facebees"),
                      ("student_coll1_1", "cows"),
                      ("teacher_coll2", "noway"),
                      ("blueshirt", "blueshirt")
                     ]

    user_objects = [User.create_user(u[0],u[1]) for u in user_passwords]
    results = [user.can_administrate(user.username) for user in user_objects]

    assert all(results)

def test_authed_teacher_can_see_own_students():
    a = User.create_user("teacher_coll1", "facebees")
    users = ["student_coll1_1", "student_coll1_2"]

    results = [a.can_administrate(user) for user in users]

    assert all(results)

def test_authed_teacher_cant_see_other_students():
    a = User.create_user("teacher_coll1", "facebees")
    users = ["student_coll2_1", "student_coll2_2"]

    results = [a.can_administrate(user) for user in users]

    assert not any(results)

def test_authed_blueshirt_can_see_own_students():
    a = User.create_user("blueshirt", "blueshirt")
    users = ["student_coll1_1", "teacher_coll1"]

    results = [a.can_administrate(user) for user in users]

    assert all(results)

def test_authed_blueshirt_cant_see_other_students():
    a = User.create_user("blueshirt", "blueshirt")
    users = ["student_coll2_2", "student_coll2_1"]

    results = [a.can_administrate(user) for user in users]

    assert not any(results)

def test_authed_teachers_cant_see_blueshirt():
    u = User.create_user("teacher_coll1", "facebees")
    u2 = User.create_user("teacher_coll2", "noway")
    users = [u, u2]
    a = User.create_user("blueshirt")

    assert not any([u.can_administrate(a) for u in users])

def test_user_properties_blueshirt():
    u = User.create_user("blueshirt", "blueshirt")
    data = u.details_dictionary_for(u)

    assert data['is_blueshirt']
    assert not data['is_student']
    assert not data['is_team_leader']

def test_user_properties_student():
    u = User.create_user("student_coll1_1", "cows")
    data = u.details_dictionary_for(u)

    assert data['is_student']
    assert not data['is_team_leader']
    assert not data['is_blueshirt']

def test_user_properties_team_leader():
    u = User.create_user("teacher_coll2", "noway")
    data = u.details_dictionary_for(u)

    assert data['is_team_leader']
    assert not data['is_student']
    assert not data['is_blueshirt']

def test_set_password():
    u = User.create_user("teacher_coll1", "facebees")
    u.set_password("bacon")
    u.save()

    u = User.create_user("teacher_coll1", "bacon")

    assert u.can_administrate("student_coll1_1")

    u.set_password("facebees")
    u.save()

def test_blueshirt_cant_see_email():
    u = User.create_user("blueshirt", "blueshirt")
    u2 = User.create_user("student_coll1_1")
    d = u2.details_dictionary_for(u)
    assert not "email" in d

def test_self_can_see_email():
    u = User.create_user("student_coll1_1", "cows")
    u2 = User.create_user("student_coll1_1")
    d = u2.details_dictionary_for(u)
    assert "email" in d

def test_manages_team_blueshirt_1():
    """Blueshirts don't manage teams"""
    u = User.create_user("blueshirt", "blueshirt")
    assert not any([u.manages_team(t) for t in u.teams])

def test_manages_team_blueshirt_2():
    """Blueshirts don't manage teams (by name)"""
    u = User.create_user("blueshirt", "blueshirt")
    assert not any([u.manages_team(t.name) for t in u.teams])

def test_manages_team_student_1():
    """Students don't manage teams"""
    u = User.create_user("student_coll1_1", "cows")
    assert not any([u.manages_team(t) for t in u.teams])

def test_manages_team_student_2():
    """Students don't manage teams (by name)"""
    u = User.create_user("student_coll1_1", "cows")
    assert not any([u.manages_team(t.name) for t in u.teams])

def test_manages_team_teacher_1():
    """Teachers manage all teams they are in"""
    u = User.create_user("teacher_coll1", "facebees")
    assert all([u.manages_team(t) for t in u.teams])

def test_manages_team_teacher_2():
    """Teachers manage all teams they are in (by name)"""
    u = User.create_user("teacher_coll1", "facebees")
    assert all([u.manages_team(t.name) for t in u.teams])

def test_manages_team_teacher_3():
    """Teachers can't manage teams they're not in"""
    u = User.create_user("teacher_coll2", "noway")
    assert not any([u.manages_team(t) for t in ['team-ABC', 'team-DFE']])

def test_manages_team_teacher_4():
    """Teachers can't manage teams they're not in (by name)"""
    u = User.create_user("teacher_coll2", "noway")
    assert not any([u.manages_team(t) for t in ['team-ABC', 'team-DFE']])

def test_manages_team_not_authed():
    """Teachers can't manage teams they're not in (by name)"""
    u = User.create_user("teacher_coll1")
    assert not any([u.manages_team(t) for t in u.teams])

def test_teacher_cant_withdraw_blueshirt():
    """Teachers can't withdraw blueshirts"""
    assert not User.create_user("teacher_coll1", "facebees").can_withdraw(User.create_user("blueshirt"))

def test_teacher_cant_withdraw_self():
    """Teachers can't withdraw themselves"""
    u = User.create_user("teacher_coll1", "facebees")
    assert not u.can_withdraw(u)

def test_only_teachers_can_withdraw():
    """Only teachers can withdraw people"""
    assert not User.create_user("student_coll1_1", "cows").can_withdraw(User.create_user("student_coll1_2"))
