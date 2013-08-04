
from os.path import abspath, dirname, join
import subprocess
import sys

# Tweak the path so we can access the config
baseDir = dirname(__file__)
there = abspath(join(baseDir, '../libnemesis'))
sys.path.insert(0, there)

from srusers.config import config

host = config.get('ldap', 'host')
username = config.get('ldap', 'username')
password = config.get('ldap', 'password')

managerDn = "cn=%s,o=sr" % (username)

if len(sys.argv) != 2:
    start_file = abspath(join(baseDir, 'ldap_start'))
else:
    start_file = sys.argv[1]

to_remove = []
with open(start_file, 'r') as lines:
    for line in lines:
        if line[:4] == 'dn: ':
            dn = line[4:].strip()
            to_remove.append(dn)

subprocess.call(['ldapdelete', '-x'
                             , '-h', host
                             , '-D', managerDn
                             , '-w', password
                ] + to_remove)


subprocess.check_call(['ldapadd', '-x'
                                , '-f', start_file
                                , '-h', host
                                , '-D', managerDn
                                , '-w', password
                      ])
