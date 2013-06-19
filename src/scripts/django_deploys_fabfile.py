import sys
from StringIO import StringIO
import datetime
import os
from fabric.api import run, env
from fabric.operations import put

import deploy_settings

env.hosts = deploy_settings.hosts
env.git_repository_command = deploy_settings.git_repository_command

env.git_branch = deploy_settings.git_branch
env.path_deploy_to = deploy_settings.path_deploy_to
env.project_directory_name = deploy_settings.project_directory_name

env.virtualenv_path = deploy_settings.virtualenv_path
env.virtualenv_name = deploy_settings.virtualenv_name

env.django_settings_file = deploy_settings.django_settings_file
env.additional_files = deploy_settings.additional_files
env.symlinks = deploy_settings.symlinks

CREATE_DIRECTORIES = ('shared', 'shared/logs', 'shared/pids',
    'shared/settings', 'releases', 'shared/virtualenv', 'shared/files',
    'shared/uploads',)

def update(repository, branch):
    base_directory = os.path.join(env.path_deploy_to, 'current')
    run('cd {0} && git pull --rebase {repository} {branch}'.format(
        base_directory, repository=repository, branch=branch))
    update_environment()
    run_migrations()

def update_environment():
    copy_files()
    update_settings_py()
    pip_install_requirements()
    update_git_submodules()

def update_git_submodules():
    base_directory = os.path.join(env.path_deploy_to, 'current')
    run('cd {0} && git submodule init && git submodule update'.format(
        base_directory))

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

def copy_files():
    copy_django_settings_file()
    copy_additional_files()

def copy_django_settings_file():
    copy_to = os.path.join(env.path_deploy_to, 'shared', 'settings')
    put(local_path=env.django_settings_file, remote_path=copy_to)

def copy_additional_files():
    if env.additional_files:
        copy_to = os.path.join(env.path_deploy_to, 'shared', 'files')
        run('touch {0}'.format(os.path.join(copy_to, '__init__.py')))
        for additional_file in env.additional_files:
            put(local_path=additional_file, remote_path=copy_to)

def update_settings_py():
    shared_settings_py_path = os.path.join(
        env.path_deploy_to,
        'shared',
        'settings',
        env.django_settings_file)
    project_path = os.path.join(
        env.path_deploy_to,
        'current',
        env.project_directory_name,
    )
    settings_py_path = os.path.join(
        project_path,
        'settings.py')
    run('rm -f {0}'.format(settings_py_path))
    run('cd {0} && ln -s {1} {2}'.format(
        project_path, shared_settings_py_path, 'settings.py'))

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
    return output

def setup_db():
    run_migrations()

def setup():
    setup_directories()
    checkout_code_and_symlink()
    create_virtualenv()
    update_environment()
    setup_db()

def deploy():
    checkout_code_and_symlink()
    update_environment()

def rollback_to(timestamp):
    create_symlink(timestamp)

def delete_release(timestamp):
    release_path = os.path.join(env.path_deploy_to, 'releases')
    delete_path = os.path.join(release_path, timestamp)
    if '..' in delete_path:
        exit(1)
    cmd_to_delete_release = 'rm -rf {0}'.format(delete_path)
    run(cmd_to_delete_release)

def symlink_files():
    if env.symlinks:
        current_path = os.path.join(env.path_deploy_to, 'current')
        shared_path = os.path.join(env.path_deploy_to, 'shared')

        for src, target in env.symlinks:
            if src[0] in ('/', '.') or target[0] in ('/', '.'):
                return

            symlink_from_path = os.path.join(shared_path, src)
            symlink_to_dir, symlink_file_name = \
                os.path.split(os.path.join(current_path, target))
            cmd = 'cd {0} && rm -f {2} && ln -s {1} {2}'.format(
                symlink_to_dir, symlink_from_path, symlink_file_name)
            run(cmd)
