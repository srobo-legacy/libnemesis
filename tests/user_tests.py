
from nose.tools import with_setup

from libnemesis import User, NullUser, srusers

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

def ensure_in_group(username, groupname):
    def helper():
        u = srusers.user(username)
        assert u.in_db
        if groupname not in u.groups():
            g = srusers.group(groupname)
            g.user_add(username)
            g.save()

    return helper

def remove_from_group(username, groupname):
    def helper():
        u = srusers.user(username)
        assert u.in_db
        if groupname in u.groups():
            g = srusers.group(groupname)
            g.user_rm(username)
            g.save()

    return helper

def test_can_make_user():
    User.create_user("teacher_coll1")

def test_nonexistant_user_raises():
    try:
        User.create_user("qowiejfqwoi")
        assert False
    except:
        pass

def check_new_user(u, first = 'first'):
    assert u.username == '1_fl1'
    assert u.first_name == first
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

def test_unicode_name_not_used():
    andre = 'Andr' + u'\xe9' # Andre with e-acute
    used = User.name_used(andre, 'Smith')
    assert used == False

def test_unicode_name_not_used_2():
    bill_pony = u'Bill\u2658' # Bill plus white chess knight
    used = User.name_used(bill_pony, 'Smith')
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

@with_setup(remove_user('to-consent'), remove_user('to-consent'))
def test_media_consent_grant():
    username = 'to-consent'
    sru = srusers.user(username)
    sru.cname = 'to'
    sru.sname = 'consent'
    sru.email = ''
    sru.save()

    u = User.create_user(username)
    # Sanity check
    assert not u.has_media_consent, "Fresh user should not have granted media consent"

    u.got_media_consent()
    u.save()
    assert u.has_media_consent, "Should have recorded the media-consent grant"

    # Fresh instance
    u = User.create_user(username)
    assert u.has_media_consent, "Media consent grant should persist"

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

def test_record_media_consent_false():
    u = User.create_user("student_coll1_1")
    assert not u.can_record_media_consent

@with_setup(remove_user('admin-consent'), remove_user('admin-consent'))
def test_media_consent_true_1():
    username = 'admin-consent'
    sru = srusers.user(username)
    sru.cname = 'admin'
    sru.sname = 'consent'
    sru.email = ''
    sru.save()

    # Sanity check
    u = User.create_user(username)
    assert not u.can_record_media_consent

    g = srusers.group('media-consent-admin')
    g.user_add(sru)
    g.save()

    u = User.create_user(username)
    assert u.can_record_media_consent

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

    u = User.create_user(username)
    u.delete()

    sru = srusers.user(username)
    assert not sru.in_db

    for gid in ['students', 'team-ABC', 'college-1']:
        g = srusers.group(gid)
        assert not username in g.members

## New user

@with_setup(remove_user('1_fl1'), remove_user('1_fl1'))
def test_new_user():
    ru = User.create_user("teacher_coll1", "facebees")
    u = User.create_new_user(ru, 'college-1', 'first', 'last')
    check_new_user(u)

@with_setup(remove_user('1_fl1'), remove_user('1_fl1'))
def test_new_user_unicode():
    ru = User.create_user("teacher_coll1", "facebees")
    first = u'f\xedrst'
    u = User.create_new_user(ru, u'college-1', first, u'last')
    check_new_user(u, first.encode('utf-8'))

@with_setup(remove_user('1_fl1'), remove_user('1_fl1'))
def test_new_user_unicode_1():
    ru = User.create_user("teacher_coll1", "facebees")
    first = u'first\u2658'
    u = User.create_new_user(ru, u'college-1', first, u'last')
    check_new_user(u, first.encode('utf-8'))

@with_setup(remove_user('1_fl1'), remove_user('1_fl1'))
def test_new_user_unicode_2():
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

## Group memberships

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

## Is Something

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

## Null User

def test_can_null_user_register_users():
    nu = NullUser()
    assert not nu.can_register_users

def test_can_null_user_other_things():
    # Not to check that it has the ability, but more that the methods exist
    nu = NullUser()
    assert not nu.can_administrate(None)
    assert not nu.can_view(None)
    assert not nu.can_withdraw(None)

## Registration Access

def test_can_plain_student_user_register_users():
    u = User.create_user('student_coll1_1')
    assert not u.can_register_users

def test_can_plain_teacher_user_register_users():
    u = User.create_user('teacher_coll1')
    assert not u.can_register_users

def test_can_plain_teacher_user_withdraw_users():
    u = User.create_user('teacher_coll1')
    s = User.create_user('student_coll1_1')
    assert not u.can_withdraw(s)

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

## Equality tests

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

## Administration

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
    u1 = User.create_user("teacher_coll1", "facebees")
    u2 = User.create_user("teacher_coll2", "noway")
    users = [u1, u2]
    a = User.create_user("blueshirt")

    assert not any([u.can_administrate(a) for u in users])

## Details for user

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

## Set Password

def test_set_password():
    u = User.create_user("teacher_coll1", "facebees")
    u.set_password("bacon")
    u.save()

    u = User.create_user("teacher_coll1", "bacon")

    assert u.can_administrate("student_coll1_1")

    u.set_password("facebees")
    u.save()

## Access rights

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

def test_teacher_cant_withdraw_self2():
    """Teachers can't withdraw themselves"""
    t = User.create_user("teacher_coll1", "facebees")
    u = User.create_user("teacher_coll1")
    assert not t.can_withdraw(u)

def test_only_teachers_can_withdraw():
    """Only teachers can withdraw people"""
    assert not User.create_user("student_coll1_1", "cows").can_withdraw(User.create_user("student_coll1_2"))

def test_unauthenticated_user_can_view_nothing():
    def helper(username, other_username):
        u = User.create_user(username)
        u1 = User.create_user(other_username)
        assert not u.can_view(u1)

    yield helper, "student_coll1_1", "student_coll1_1"
    yield helper, "student_coll1_1", "teacher_coll1"
    yield helper, "student_coll1_1", "blueshirt"
    yield helper, "teacher_coll1", "student_coll1_1"
    yield helper, "teacher_coll1", "teacher_coll1"
    yield helper, "teacher_coll1", "blueshirt"
    yield helper, "blueshirt", "student_coll1_1"
    yield helper, "blueshirt", "teacher_coll1"
    yield helper, "blueshirt", "blueshirt"

def test_can_view_self():
    def helper(username, password):
        u = User.create_user(username, password)
        u1 = User.create_user(username, password)
        assert u.can_view(u), "should be able to same instance"
        assert u.can_view(u1), "should be able to see other authenticated self"
        u2 = User.create_user(username)
        assert u.can_view(u2), "should be able to see other plain self"

    yield helper, "student_coll1_1", "cows"
    yield helper, "teacher_coll1", "facebees"
    yield helper, "blueshirt", "blueshirt"

def test_can_view_other():
    def helper(username, password, other_username):
        u = User.create_user(username, password)
        other = User.create_user(other_username)
        assert u.can_view(other)

    yield helper, "teacher_coll1", "facebees", "student_coll1_1"
    yield helper, "blueshirt", "blueshirt", "student_coll1_1"
    yield helper, "blueshirt", "blueshirt", "teacher_coll1"

def test_can_not_view_other():
    def helper(username, password, other_username, description):
        u = User.create_user(username, password)
        other = User.create_user(other_username)
        assert not u.can_view(other), description

    yield helper, "student_coll1_1", "cows", "teacher_coll1", "students shouldn't see teachers"
    yield helper, "student_coll1_1", "cows", "blueshirt", "students shouldn't see blueshirts"
    yield helper, "student_coll1_1", "cows", "student_coll1_2", "students shouldn't see other students"
    yield helper, "student_coll1_1", "cows", "student_coll2_2", "students shouldn't see other students"

    yield helper, "teacher_coll1", "facebees", "student_coll2_2", "teachers shouldn't see other team's students"
    yield helper, "teacher_coll1", "facebees", "blueshirt", "teachers shouldn't see blueshirts"
    yield helper, "blueshirt", "blueshirt", "student_coll2_2", "blueshirts shouldn't see other team's students"

def test_blueshirt_extra_can_view_all_competitors():
    def helper(other_username):
        u = User.create_user("blueshirt-extra", "blueshirt")
        other = User.create_user(other_username)
        assert u.can_view(other)

    yield helper, "student_coll1_1"
    yield helper, "student_coll2_2"
    yield helper, "teacher_coll1"
    yield helper, "teacher_coll2"

def test_media_consent_admin_can_view_all_competitors():
    blueshirt_mcf = srusers.user('blueshirt-mcf')
    groups = blueshirt_mcf.groups()
    # Sanity check
    assert set(groups) == set(['mentors', 'media-consent-admin'])

    def helper(other_username):
        u = User.create_user("blueshirt-mcf", "blueshirt")
        other = User.create_user(other_username)
        assert u.can_view(other)

    yield helper, "student_coll1_1"
    yield helper, "student_coll2_2"
    yield helper, "teacher_coll1"
    yield helper, "teacher_coll2"

def test_blueshirt_extra_details():
    def helper(other_username):
        blueshirt = User.create_user("blueshirt-extra", "blueshirt")
        competitor = User.create_user(other_username)
        assert blueshirt.can_view(competitor), "Sanity check"
        details = competitor.details_dictionary_for(blueshirt)
        for keyname in ["username", "first_name", "last_name", "is_student", \
                        "is_team_leader", "has_withdrawn", "has_media_consent", \
                        "teams", "colleges"]:
            assert keyname in details

        assert not 'email' in details, "No need to be able to see their email"

    yield helper, "student_coll1_1"
    yield helper, "student_coll2_2"
    yield helper, "teacher_coll1"
    yield helper, "teacher_coll2"
