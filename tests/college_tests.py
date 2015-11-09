
import time
from nose.tools import with_setup

from libnemesis import College, srusers

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

def test_college_neq_works():
    c = College("college-1")
    c2 = College("college-2")

    assert c != c2

def test_college_neq_string_works():
    c = College("college-1")
    c2 = "college-2"

    assert c != c2

def test_all_colleges():
    assert len(College.all_college_names()) == 2

def test_load_speed():
    c = College("college-3")

    t = time.time()
    c.users
    e = time.time()
    print e-t
    assert e-t < 1
