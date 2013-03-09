from libnemesis import Team

def test_team_has_right_users():
    t = Team("team-ABC")
    assert set([u.username for u in t.users]) == set(["teacher_coll1", "student_coll1_1"])

