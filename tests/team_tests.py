from libnemesis import Team

def test_team_has_right_users():
    t = Team("team-ABC")
    users = set(u.username for u in t.users)
    expected = set(["teacher_coll1", "student_coll1_1", "withdrawn_student"])
    assert users == expected

def test_team_not_eq_none():
    t = Team('team-ABC')
    assert t != None

def test_team_name():
    t = Team('team-ABC')
    assert t.name == 'team-ABC'

def test_team_not_eq_string():
    t = Team('team-ABC')
    assert t != 'team-ABC'

def test_team_not_eq_other_team():
    t1 = Team('team-ABC')
    t2 = Team('team-DEF')
    assert t1 != t2

def test_team_not_eq_self():
    t1 = Team('team-ABC')
    assert (t1 != t1) is False

def test_team_eq_equivalent_instance():
    t1 = Team('team-ABC')
    t2 = Team('team-ABC')
    assert t1 == t2
