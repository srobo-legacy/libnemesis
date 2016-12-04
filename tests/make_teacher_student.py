
from nose.tools import with_setup

from libnemesis import User, srusers

def my_setUp():
    # Create a temp user
    sru = srusers.user('st_user1')
    sru.email = 'st_user1@example.com'
    sru.cname = 'steve'
    sru.sname = 'user1'
    sru.save()

def my_tearDown():
    # Remove the temp user & its memberships
    sru = srusers.user('st_user1')
    groups = sru.groups()
    if sru.delete():
        for g in groups:
            srg = srusers.group(g)
            srg.user_rm('st_user1')
            srg.save()

@with_setup(my_setUp, my_tearDown)
def test_make_student_teacher():
    students = srusers.group('students')
    students.user_add('st_user1')
    students.save()

    u = User.create_user('st_user1')
    u.make_teacher()
    u.save()

    assert u.is_teacher

    teachers = srusers.group('teachers').members
    assert 'st_user1' in teachers

    students = srusers.group('students').members
    assert 'st_user1' not in students

@with_setup(my_setUp, my_tearDown)
def test_make_teacher():
    u = User.create_user('st_user1')
    u.make_teacher()
    u.save()

    assert u.is_teacher

    teachers = srusers.group('teachers').members
    assert 'st_user1' in teachers

    students = srusers.group('students').members
    assert 'st_user1' not in students

@with_setup(my_setUp, my_tearDown)
def test_make_teacher_student():
    teachers = srusers.group('teachers')
    teachers.user_add('st_user1')
    teachers.save()

    u = User.create_user('st_user1')
    u.make_student()
    u.save()

    assert not u.is_teacher

    students = srusers.group('students').members
    assert 'st_user1' in students

    teachers = srusers.group('teachers').members
    assert 'st_user1' not in teachers

@with_setup(my_setUp, my_tearDown)
def test_make_student():
    u = User.create_user('st_user1')
    u.make_student()
    u.save()

    assert not u.is_teacher

    students = srusers.group('students').members
    assert 'st_user1' in students

    teachers = srusers.group('teachers').members
    assert 'st_user1' not in teachers
