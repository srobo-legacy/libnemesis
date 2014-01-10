from libnemesis import Team

def test_team_has_right_users():
    t = Team("team-ABC")
    users = set(u.username for u in t.users)
    expected = set(["teacher_coll1", "student_coll1_1", "withdrawn_student"])
    assert users == expected

