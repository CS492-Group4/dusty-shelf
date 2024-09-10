import os
import zipfile
from tempfile import NamedTemporaryFile, mkdtemp
import requests
import re
import ctypes
import tempfile
import uuid
from bs4 import BeautifulSoup
from dockerfile_parse import DockerfileParser


def isAdmin():
    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_admin


def get_filename_from_cd(cd):
    """
    Get filename from content-disposition
    """
    if not cd:
        return None
    fname = re.findall('filename=(.+)', cd)
    if len(fname) == 0:
        return None
    return fname[0]

def projectPath(localdata=None):
    parents = os.getcwd().split(os.sep)
    for i in range(len(parents)):
        if i == 0:
            parents_list = parents
        else:
            parents_list = parents[:-i]

        config_path = os.sep.join(parents_list + ['config.json'])

        if os.path.exists(config_path):
            if localdata is None:
                return os.sep.join(parents_list)

            return os.sep.join(parents_list + [localdata])
    return None

def unzip(key, directory):
    f = NamedTemporaryFile(delete=False)
    f.close()
    fn = f.name

    url = 'https://s3.amazonaws.com/whl/{key}'.format(key=key)
    r = requests.get(url, allow_redirects=True)
    with open(fn, 'wb') as f:
        f.write(r.content)

    file_name = os.path.abspath(fn)  # get full path of files
    zip_ref = zipfile.ZipFile(file_name)  # create zipfile object

    if not os.path.exists(directory):
        os.mkdir(directory)

    zip_ref.extractall(directory)  # extract file to dir
    zip_ref.close()  # close file
    os.unlink(file_name)  # delete zipped file

def install_data(ctx, name=None, target=None):
    project_fn = projectPath()
    if name is None:
        name = os.path.basename(project_fn)

    zipfn = os.path.join(tempfile.gettempdir(), 'z'+str(uuid.uuid4()).replace('-','')+'.zip')
    import urllib.request

    url = "https://s3.amazonaws.com/whl/data/{name}/data.zip".format(name=name)
    urllib.request.urlretrieve(url, zipfn)

    zip_ref = zipfile.ZipFile(zipfn, 'r')
    if target is None:
        target = 'localdata'
    zip_ref.extractall(os.path.join(projectPath(), target))
    zip_ref.close()
    os.unlink(zipfn)


def install_private_package(ctx, package, secret):
    admin = ctx.obj['admin']

    # extra-index-url -> index-url
    if secret is None:
        os.system("pip install {package} --quiet --no-cache  --no-cache-dir --upgrade --extra-index-url http://s3.amazonaws.com/whl/{package}/index.html --find-links http://s3.amazonaws.com/whl/{package}/index.html --trusted-host s3.amazonaws.com".format(package=package))
    else:
        os.system("pip install {package} --quiet --no-cache  --no-cache-dir --upgrade --extra-index-url http://s3.amazonaws.com/whl/{secret}/{package}/index.html --find-links http://s3.amazonaws.com/whl/{secret}/{package}/index.html --trusted-host s3.amazonaws.com".format(package=package, secret=secret))

    if admin:
        os.system("pipz --admin install-requirements {package}".format(package=package))
    else:
        os.system("pipz --no-admin install-requirements {package}".format(package=package))

    os.system('pip show {package}'.format(package=package))

def get_private_package_version(ctx, package, secret):
    if secret is None:
        url = 'https://s3.amazonaws.com/whl/{package}/index.html'.format(package=package)
    else:
        url = 'http://s3.amazonaws.com/whl/{secret}/{package}/index.html'.format(package=package, secret=secret)

    import urllib.request
    contents = urllib.request.urlopen(url)
    soup = BeautifulSoup(contents, 'lxml')
    for link in soup.findAll('a'):
        aa = link.get('href')
        parts = aa.split('-')
        id = parts.index('py2.py3') - 1
        version = parts[id]
        return version
    raise Exception('Not found: {package} {secret}'.format(package=package, secret=secret))


def download_private_package(ctx, package, secret):
    admin = ctx.obj['admin']
    if secret is None:
        os.system("pip download {package} --no-cache  --no-cache-dir --no-deps --index-url http://s3.amazonaws.com/whl/{package}/index.html --find-links http://s3.amazonaws.com/whl/{package}/index.html --trusted-host s3.amazonaws.com".format(package=package))
    else:
        os.system("pip download {package} --no-cache  --no-cache-dir --no-deps  --index-url http://s3.amazonaws.com/whl/{secret}/{package}/index.html --find-links http://s3.amazonaws.com/whl/{secret}/{package}/index.html --trusted-host s3.amazonaws.com".format(package=package, secret=secret))

if __name__ == '__main__':

    d = DockerfileParser(r'G:\jmull\Downloads\images.tar\images\rsm\Dockerfile')
    print(get_private_package_version({}, 'knowhen', '2018'))