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
