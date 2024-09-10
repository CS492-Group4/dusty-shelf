import click
import os
from .pipzlib import get_private_package_version, install_private_package, download_private_package, isAdmin, install_data
#import subprocess
import sys
import getpass
import pkg_resources
import re

import tempfile
import shutil
from .run_utils import run
from .docker_utils import make_images, get_build_image_chain, get_all_images
def common_libs():
    os.system('pip3 install ipywidgets')
    os.system('pip3 install cufflinks')
    os.system('pip3 install git+https://github.com/altair-viz/jupyter_vega')
    os.system('conda install -y bokeh')

def splitall(fn):
    parts = fn.split('/')
    real_parts = []
    for p in parts:
        real_parts += p.split('\\')
    return real_parts




@click.group(invoke_without_command=True)
@click.option('--admin/--no-admin', default=False)
@click.option('--upgrade', default=False, is_flag=True)
@click.pass_context
def cli(ctx, admin, upgrade):
    if ctx.obj is None:
        ctx.obj = {}
    ctx.obj['admin'] = admin
    ctx.obj['upgrade'] = upgrade
    if admin and not isAdmin():
        raise Exception('Run the command with elevated priviledges.')

    nothing = True

    if upgrade:
        nothing = False
        status, output = run('pip3 install --upgrade --no-cache --no-cache-dir pipz')
        sys.exit(status)


@cli.command(name='install')
@click.argument('package')
@click.option('--secret', default=None)
@click.pass_context
def install(ctx, package, secret):
    if secret is None:
        secret = getpass.getpass()
    install_private_package(ctx, package, secret)

@cli.command(name='remote-version')
@click.option('--package', '-p', nargs=2, type=click.Tuple([str, str]), multiple=True)
@click.pass_context
def remote_version(ctx, package):
    result = {}
    for p in package:
        v = get_private_package_version(ctx, p[0], p[1])
        result[p[0]] = v
    print(result)



@cli.command(name='install-data')
@click.option('--package', default=None)
@click.option('--location', default='localdata')
@click.pass_context
def install_module(ctx, package, location):
    install_data(ctx, package, location)

@cli.command(name='install-requirements')
@click.argument('package')
@click.pass_context
def install_requirements(ctx, package):
    pipz_path = os.path.dirname(os.path.dirname(__import__('pipz').__file__))
    file = os.path.join(pipz_path, package, 'z-requirements.py')
    if not os.path.exists(file):
        return
    if os.path.exists(file):
        with open(file) as fp:
            for cnt, line in enumerate(fp):
                line = line[1:].strip()
                if line.startswith('run '):
                    ll = line[len('run '):]
                    os.system(ll)
                    continue

                if line.startswith('winrun ') and (sys.platform == "win32"):
                    ll = line[len('winrun '):]
                    os.system(ll)
                    continue

                if line.startswith('linrun ') and (sys.platform != "win32"):
                    ll = line[len('linrun '):]
                    os.system(ll)
                    continue


                if len(line) == 0 or line.startswith('#') or line.startswith(';'):
                    continue
                try:
                    package, secret = [x.strip() for x in line.split('--secret')]

                    if package.startswith('module:'):
                        print('module skipped')
                    else:
                        install_private_package(ctx, package, secret)
                except Exception as e:
                    print("Error installing: {}".format(line))
                    print(e)
        return

    print('{} does not exist.'.format(file))


@cli.command(name='uninstall')
@click.argument('package')
@click.pass_context
def uninstall(ctx, package):
    os.system('pip3 uninstall {}'.format(package))


@cli.command(name='download')
@click.argument('package')
@click.option('--secret', default=None)
@click.option('--unzip', default=False)
@click.pass_context
def download(ctx, package, secret, unzip):
    if secret is None:
        secret = getpass.getpass()
    download_private_package(ctx, package, secret)
    if unzip:
        print('Unzip is not supported your. Please unzip the file manually')

@cli.command(name='ps')
@click.option('--str', default='')
@click.option('--process', default='')
@click.option('--down', default=False, is_flag=True)
@click.pass_context
def ps(ctx, str, process, down):
    cmd = 'powershell "Get-WmiObject -Class Win32_process'
    if process:
        cmd += '| ? {$_.Name -eq \'' + process + '\'}  '

    if str:
        cmd += '| ?{$_.CommandLine -like \'*' + str + '*\'} '

    cmd += '| ?{-not ($_.CommandLine  -like \'*get-wimobject*\')}| ?{-not ($_.CommandLine  -like \'*pipz  ps*\')}| ?{-not ($_.CommandLine  -like \'*pipz.exe*\')}|select processid, commandline'

    os.system(cmd)

    if down:
        os.system(cmd + '|foreach {stop-Process  -ID $_.ProcessId}')

@cli.command(name='build-chain')
@click.option('--build', default=None)
@click.option('--repo', default=None)
@click.option('--path', default=None)
@click.option('--since', default=None)
@click.option('--dryrun', is_flag=True)
@click.pass_context
def docker_tree(ctx, build,  dryrun, since, repo, path):


    if repo is None and path is None:
        path = os.getcwd()

    clear_path = False
    if repo is not None:
        tmpdir = tempfile.mkdtemp()

        clone_cmd = 'git clone {repo} {tmpdir}'.format(repo=repo, tmpdir=tmpdir)
        os.system(clone_cmd)
        tmpdirs = [tmpdir]
        if path is not None:
            tmpdirs += [path]

        path = '/'.join(tmpdirs)

    images = get_all_images(path)
    images_chain = get_build_image_chain(images, build, since)
    make_images(images_chain, dryrun=dryrun)

    if clear_path:
        shutil.rmtree(tempfile, ignore_errors=True)




if __name__ == '__main__':
    cli(obj={'ok':1})
