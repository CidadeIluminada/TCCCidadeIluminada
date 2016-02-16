# coding: UTF-8
from __future__ import absolute_import

from fabtools import require, files, python
from fabtools.python import virtualenv

from fabric.api import env, sudo, cd, settings

env.host_string = 'root@45.55.6.21'

CIDADEILUMINADA_WORK_PATH = '/root/cidadeiluminada/'
CIDADEILUMINADA_REPO_PATH = 'git@github.com:HardDiskD/TCCCidadeIluminada.git'


def teardown():
    with settings(warn_only=True):
        files.remove(CIDADEILUMINADA_WORK_PATH, use_sudo=True, recursive=True)


def setup():
    require.git.working_copy(CIDADEILUMINADA_REPO_PATH, path=CIDADEILUMINADA_WORK_PATH, update=True)
    with cd(CIDADEILUMINADA_WORK_PATH):
        require.files.directories(['instance'], use_sudo=True)
        require.python.virtualenv(CIDADEILUMINADA_WORK_PATH)
        with virtualenv(CIDADEILUMINADA_WORK_PATH):
            python.install('uwsgi')
    deploy()
    with cd(CIDADEILUMINADA_WORK_PATH), virtualenv(CIDADEILUMINADA_WORK_PATH):
        sudo('python manage.py ci criar_usuarios')
        sudo('uwsgi --socket :8080 --module="cidadeiluminada:create_app()" --touch-reload="/root/uwsgi_file"')


def deploy():
    require.git.working_copy(CIDADEILUMINADA_REPO_PATH, path=CIDADEILUMINADA_WORK_PATH, update=True)
    with cd(CIDADEILUMINADA_WORK_PATH), virtualenv(CIDADEILUMINADA_WORK_PATH):
        require.python.requirements('requirements.txt')
        require.python.requirements('requirements-db.txt')
        sudo('python manage.py db upgrade')
    reload()


def reload():
    sudo('touch /root/uwsgi_file')
