import sys
from StringIO import StringIO
import datetime
import os
from fabric.api import run, env
from fabric.operations import put

import deploy_settings
from gunicorn_settings import options, wsgi_application

env.hosts = deploy_settings.hosts
env.git_repository_command = deploy_settings.git_repository_command

env.git_branch = deploy_settings.git_branch
env.path_deploy_to = deploy_settings.path_deploy_to

env.virtualenv_path = deploy_settings.virtualenv_path
env.virtualenv_name = deploy_settings.virtualenv_name

env.setting_files = deploy_settings.setting_files

CREATE_DIRECTORIES = ('shared', 'shared/logs', 'shared/pids',
    'shared/settings', 'releases', 'shared/virtualenv',)

def update_environment():
    copy_settings()
    pip_install_requirements()

def create_virtualenv():
    run('cd {0} && virtualenv --no-site-packages {1}'.format(
        env.virtualenv_path, env.virtualenv_name))

def pip_install_requirements():
    virtualenv_activate_path = os.path.join(
        env.virtualenv_path, env.virtualenv_name, 'bin', 'activate')
    requirements_path = os.path.join(env.path_deploy_to, 'current',
        'requirements.txt')
    run('source {0} && pip install -r {1}'.format(
        virtualenv_activate_path, requirements_path))

def run_migrations():
    virtualenv_activate_path = os.path.join(
        env.virtualenv_path, env.virtualenv_name, 'bin', 'activate')
    migrate_cmd = \
        'source {0} && cd {1} && python manage.py syncdb && python manage.py migrate'
    migrate_location = os.path.join(env.path_deploy_to, 'current')
    run(migrate_cmd.format(virtualenv_activate_path, migrate_location))

def copy_settings():
    copy_to = os.path.join(env.path_deploy_to, 'shared', 'settings')
    run('touch {0}'.format(os.path.join(copy_to, '__init__.py')))
    for setting_file in env.setting_files:
        put(local_path=setting_file, remote_path=copy_to)

def update_settings_py(project):
    production_settings_py_path = os.path.join(
        env.path_deploy_to,
        'current',
        project,
        'settings.production.py')
    settings_py_path = os.path.join(
        env.path_deploy_to,
        'current',
        project,
        'settings.py')
    run('rm -f {0}'.format(settings_py_path))
    run('ln -s {0} {1}'.format(
        production_settings_py_path, settings_py_path))

def start_gunicorn():
    sys.path.append(os.path.abspath(os.path.dirname(__file__)))
    virtualenv_activate_path = os.path.join(
        env.virtualenv_path, env.virtualenv_name, 'bin', 'activate')
    gunicorn_flags = \
        ' '.join(['--%s=%s' % (k,v,) for k,v in options.items()])
    gunicorn_cmd = 'source {0} && cd {1} && PYTHONPATH={2} gunicorn -D {3} {4}'.format(
        virtualenv_activate_path,
        env.path_deploy_to,
        os.path.join(env.path_deploy_to, 'current'),
        gunicorn_flags,
        wsgi_application)
    run(gunicorn_cmd)

def restart_gunicorn():
    stop_gunicorn()
    start_gunicorn()

def reload_gunicorn():
    pid_location = os.path.join(env.path_deploy_to, 'shared', 'pids', 'gunicorn.pid')
    gunicorn_cmd = 'kill -HUP `cat {0}`'.format(pid_location)
    run(gunicorn_cmd)

def stop_gunicorn():
    pid_location = os.path.join(env.path_deploy_to, 'shared', 'pids', 'gunicorn.pid')
    gunicorn_cmd = 'kill `cat {0}`'.format(pid_location)
    run(gunicorn_cmd)

def setup_directories():
    for directory in CREATE_DIRECTORIES:
        path = os.path.join(env.path_deploy_to, directory)
        run('mkdir -p {0}'.format(path))

def has_current_symlink():
    output = StringIO()
    symlink_path = os.path.join(env.path_deploy_to, 'current')
    file_exists_cmd = \
        'python -c \'import os; print os.path.islink("{0}")\''.format(symlink_path)
    run(file_exists_cmd, stdout=output)
    return (u'False' not in output.getvalue().strip())

def remove_symlink():
    symlink_path = os.path.join(env.path_deploy_to, 'current')
    run('rm {0}'.format(symlink_path))

def create_symlink(timestamp):
    deploy_to_release_path = os.path.join(
        env.path_deploy_to, 'releases', timestamp)
    symlink_path = os.path.join(env.path_deploy_to, 'current')
    if has_current_symlink():
        remove_symlink()
    run('ln -s {0} {1}'.format(deploy_to_release_path, symlink_path))

def checkout_code_and_symlink():
    timestamp = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')
    deploy_to_release_path = os.path.join(
        env.path_deploy_to, 'releases', timestamp)
    run('git clone -b {0} {1} {2}'.format(
        env.git_branch,
        env.git_repository_command,
        deploy_to_release_path))
    create_symlink(timestamp)

def last_timestamp(from_tail=1):
    output = StringIO()
    release_path = os.path.join(env.path_deploy_to, 'releases')
    #most_recent_timestamp_cmd = \
    #    "ls -altr {0} | cut -d" " -f 10 | tail -n 1".format(release_path)
    most_recent_timestamp_cmd = \
        'PYTHONIOENCODING="utf-8" ls --color=never -Altr {0} | python -c \'import sys; import re; print [re.split(r"\d\d:\d\d", s)[1].strip() for s in unicode(sys.stdin.read(), "utf-8").split("\\n") if re.search(r"\d\d:\d\d", s)][{1}]\''.strip().format(release_path, int(from_tail)*-1)
    release_date = run(most_recent_timestamp_cmd, stdout=output)
    print 'last created timestamp = %s' % output.getvalue()
    return output

def setup_db():
    run_migrations()

def setup():
    setup_directories()
    checkout_code_and_symlink()
    create_virtualenv()
    update_environment()
    setup_db()
    start_gunicorn()

def deploy():
    checkout_code_and_symlink()
    update_environment()
    reload_gunicorn()

def rollback_to(timestamp):
    create_symlink(timestamp)

def delete_release(timestamp):
    release_path = os.path.join(env.path_deploy_to, 'releases')
    delete_path = os.path.join(release_path, timestamp)
    if '..' in delete_path:
        print '.. is in delete_path'
        exit(1)
    cmd_to_delete_release = 'rm -rf {0}'.format(delete_path)
    run(cmd_to_delete_release)
