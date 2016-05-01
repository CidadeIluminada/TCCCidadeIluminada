# coding: UTF-8
from __future__ import absolute_import

import os

from fabtools import require, files, python
from fabtools.python import virtualenv

from fabric.api import env, sudo, cd, settings

env.host_string = 'root@104.236.157.40'

CIDADEILUMINADA_WORK_PATH = '/root/cidadeiluminada/'
CIDADEILUMINADA_REPO_PATH = 'git@github.com:CidadeIluminada/TCCCidadeIluminada.git'


def teardown():
    with settings(warn_only=True):
        files.remove(CIDADEILUMINADA_WORK_PATH, use_sudo=True, recursive=True)


def create_settings_local():
    with cd(CIDADEILUMINADA_WORK_PATH), virtualenv(CIDADEILUMINADA_WORK_PATH):
        instance_path = sudo('python manage.py instance_path')
    require.files.directories([instance_path], use_sudo=True)
    settings_path = os.path.join(CIDADEILUMINADA_WORK_PATH, 'settings.py')
    settings_local_path = os.path.join(instance_path, 'settings_local.py')
    files.copy(settings_path, settings_local_path, use_sudo=True)


def setup():
    require.git.working_copy(CIDADEILUMINADA_REPO_PATH, path=CIDADEILUMINADA_WORK_PATH, update=True)
    with cd(CIDADEILUMINADA_WORK_PATH):
        require.python.virtualenv(CIDADEILUMINADA_WORK_PATH)
        with virtualenv(CIDADEILUMINADA_WORK_PATH):
            python.install('uwsgi')
    create_settings_local()


def finish_setup():
    deploy()
    with cd(CIDADEILUMINADA_WORK_PATH), virtualenv(CIDADEILUMINADA_WORK_PATH):
        sudo('python manage.py ci criar_usuarios')
        sudo('uwsgi --socket :8080 --module="cidadeiluminada:create_app()" --touch-reload="/root/uwsgi_file"')


def deploy():
    require.git.working_copy(CIDADEILUMINADA_REPO_PATH, path=CIDADEILUMINADA_WORK_PATH, update=True)
    with cd(CIDADEILUMINADA_WORK_PATH), virtualenv(CIDADEILUMINADA_WORK_PATH):
        require.python.requirements('requirements.txt')
        sudo('python manage.py db upgrade')
    reload()


def reload():
    sudo('touch /root/uwsgi_file')
