from fabric.api import cd, env, put
from fabric.operations import run
import time
from config import HOSTS, USER, SSH_PRIVATE_KEY_FILE, SSH_PORT, REMOTE_SOURCE_DIRECTORY


env.hosts = HOSTS
env.user = USER
env.key_filename = SSH_PRIVATE_KEY_FILE
env.port = SSH_PORT


def config():
    with cd('/etc/supervisor/conf.d/'):
        put('./bigdipper.conf', './')
        run('supervisorctl reread')
        run('supervisorctl update')
        run('supervisorctl start bigdipper1')
        time.sleep(30)
        run('supervisorctl start bigdipper2')
        run('supervisorctl start twitterfeed')


def deploy():
    with cd(REMOTE_SOURCE_DIRECTORY):
        run("git pull")
    run('supervisorctl restart bigdipper1')
    time.sleep(30)
    run('supervisorctl restart bigdipper2')
    run('supervisorctl restart twitterfeed')


def status():
    run('supervisorctl status')