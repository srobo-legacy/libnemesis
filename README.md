#LibNemesis

This is LibNemesis, primarliy intended as a backing library to
[Nemesis](http://github.com/samphippen/nemesis), it provides high level
functionality for organising users within a [Student Robotics](http://studentrobotics.org)
[LDAP](https://www.studentrobotics.org/trac/wiki/LDAP) database.


##Contributing

Please file issues on GitHub. Not on the Student Robotics trac. Also please
send me a GitHub pull request if you want to merge changes in. This allows
for easy management in my brain.

##Development

You almost certainly want to develop LibNemesis in the context of Nemesis,
so see that repo for instructions on getting going.

In the even that you're doing something else, you'll need to init the
submodules: `git submodule update --init`, and an SR LDAP you can point at.
The target database can be set by modifying the config of the srusers
submodule, usually by adding a local.ini.

##Tests

Everything should have tests to ensure that it behaves suitably, and any
new functionality should have tests to match. You should also ensure that
the tests all pass for you before starting development, as otherwise you'll
have a hard time figuring out what caused any breakages.

The tests can be run via the `run-tests` script in the root of the repo.
This will clear the configured LDAP of any entries that are needed for the
tests, and then create them with the expected value.

The reset is achieved by the `tests/reset_ldap.py` script, which uses the
 `tests/start_ldap` file as a basis for the tests' expectations.
If you need any other items to be in the database for simple testing,
 this is where they should be added.
Tests which need to modify items should create them on the fly to ensure
that other tests can still rely on this base environment.
