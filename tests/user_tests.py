from libnemesis import *

def test_can_make_user():
    User.create_user("teacher_coll1")

def test_nonexistant_user_raises():
    try:
        User.create_user("qowiejfqwoi")
        assert False
    except:
        pass

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

def test_is_blueshirt_1():
    assert not User.create_user("student_coll2_1").is_blueshirt

def test_is_blueshirt_2():
    assert not User.create_user("teacher_coll1").is_blueshirt

def test_is_blueshirt_3():
    assert User.create_user("blueshirt").is_blueshirt

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
