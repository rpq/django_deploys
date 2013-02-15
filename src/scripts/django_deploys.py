#!/home/rpq/.python-ves/djangodeploy/bin/python

import os
import sys
import subprocess

if __name__ == '__main__':
    os.environ['PYTHONPATH'] = '.'
    fab_location = subprocess.check_output('which fab'.split(' '))
    fab_location = fab_location.strip()
    fab_deploy_cmd = []
    fab_deploy_cmd.append(fab_location)
    fab_deploy_cmd.append('-f')
    fab_deploy_cmd.append('{0}/django_deploys_fabfile.py'.format(
        os.path.dirname(fab_location)))
    fab_deploy_cmd.extend(sys.argv[1:])
    fab_deploy_cmd = ' '.join(fab_deploy_cmd)
    os.system(fab_deploy_cmd)
