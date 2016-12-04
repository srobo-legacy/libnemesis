
import time
from nose.tools import assert_raises, with_setup

from libnemesis import College, User, srusers

def add_blueshirt_to_team_QWZ():
    g = srusers.group("team-QWZ")
    g.user_add("blueshirt")
    g.save()

def remove_blueshirt_from_team_QWZ():
    g = srusers.group("team-QWZ")
    g.user_rm("blueshirt")
    g.save()

def test_college_has_correct_users():
    c = College("college-1")
    users = set([u.username for u in c.users])
    eu = set(["teacher_coll1", "student_coll1_1", "student_coll1_2", \
                "blueshirt", "withdrawn_student"])

    assert users == eu

def test_college_has_correct_name():
    c = College("college-1")
    assert c.name == "college the first"

def test_college_has_correct_teams():
    c = College("college-1")
    actual = set([t.name for t in c.teams])
    assert actual == set(["team-ABC", "team-DFE"])

@with_setup(add_blueshirt_to_team_QWZ, remove_blueshirt_from_team_QWZ)
def test_college_has_correct_teams_with_blueshirt():
    c = College("college-1")
    actual = set([t.name for t in c.teams])
    assert actual == set(["team-ABC", "team-DFE"])

def test_college_eq_works():
    c = College("college-1")
    c2 = College("college-1")
    assert c == c2

def test_college_eq_string_works():
    c = College("college-1")
    c2 = "college-1"

    assert c == c2

def test_college_neq_works_other():
    c = College("college-1")
    c2 = College("college-2")

    assert c != c2

def test_college_neq_works_self():
    c = College("college-1")

    assert (c != c) is False

def test_college_neq_string_works_other():
    c = College("college-1")
    c2 = "college-2"

    assert c != c2

def test_college_neq_string_works_self():
    name = "college-1"
    c = College(name)

    assert (c != name) is False

def test_all_colleges():
    assert len(College.all_college_names()) == 2

def test_load_speed():
    c = College("college-3")

    t = time.time()
    c.users
    e = time.time()
    print e-t
    assert e-t < 1

def assert_college_1_details_dictionary_for(requesting_user):
    c = College("college-1")
    data = c.details_dictionary_for(requesting_user)

    actual_name = data["name"]
    assert actual_name == "college the first"

    actual_teams = data["teams"]
    assert actual_teams == ["team-ABC", "team-DFE"]

    actual_counts = data["counts"]
    expected_counts = {
        'team_leaders': 1,
        'students': 3,
        'media_consent': 0,
        'withdrawn': 1,
    }
    assert actual_counts == expected_counts

    return data

def test_details_dictionary_for_student_member():
    u = User.create_user("student_coll1_1")
    data = assert_college_1_details_dictionary_for(u)

    actual_users = data["users"]
    assert actual_users == []

def test_details_dictionary_for_team_leader_member():
    u = User.create_user("teacher_coll1", "facebees")
    data = assert_college_1_details_dictionary_for(u)

    expected_users = [
        "teacher_coll1",
        "student_coll1_1",
        "student_coll1_2",
        "withdrawn_student",
    ]
    actual_users = data["users"]
    assert actual_users == expected_users

def test_details_dictionary_for_blueshirt_member():
    u = User.create_user("blueshirt", "blueshirt")
    data = assert_college_1_details_dictionary_for(u)

    expected_users = [
        "teacher_coll1",
        "student_coll1_1",
        "student_coll1_2",
        "blueshirt",
        "withdrawn_student",
    ]
    actual_users = data["users"]
    assert actual_users == expected_users

def test_details_dictionary_for_blueshirt_non_member():
    u = User.create_user("blueshirt")
    c = College("college-2")
    data = c.details_dictionary_for(u)

    actual_name = data["name"]
    assert actual_name == "secondary college"

    actual_teams = data["teams"]
    assert actual_teams == ["team-QWZ"]

    assert "users" not in data

    actual_counts = data["counts"]
    expected_counts = {
        'team_leaders': 1,
        'students': 2,
        'media_consent': 0,
        'withdrawn': 0,
    }
    assert actual_counts == expected_counts


def test_details_dictionary_for_non_member():
    c = College("college-1")
    u = User.create_user("student_coll2_1")

    with assert_raises(AssertionError):
        c.details_dictionary_for(u)
