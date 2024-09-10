import glob2
from dockerfile_parse import DockerfileParser
import os
from .run_utils import run


def get_all_images(folder, owner='jmulla'):
    '''
    Scans the folder for all Dockerfiles and builds a dependency tree
    :param folder:
    :return:
    '''
    is_absolute_path = True
    wd_pars = folder.split(os.sep)
    images = []
    for df in glob2.iglob('{folder}/**/Dockerfile'.format(folder=folder)):
        df_parts = df.split(os.sep)
        docker_image = '{owner}/{aa}'.format(owner=owner, aa=df_parts[-2])
        d = DockerfileParser(df)
        from_info, = [x for x in d.structure if x['instruction'] == 'FROM']
        parent = from_info['value']
        images.append({
            'image': docker_image,
            'parent': parent,
            'dockerfile':df
        })

    return images

def get_build_image_chain(images, image_name, since=None):
    sorted_images = []
    image, = [x for x in images if x['image'] == image_name]
    sorted_images.append(image)

    while since is not None and image['image'] != since:
        image_name = image['parent']
        image, = [x for x in images if x['image'] == image_name]
        sorted_images.append(image)

    return sorted_images[::-1]

def make_images(image_chain, dryrun=False, tags=[]):
    for image in image_chain:
        result = make_image(image, dryrun=dryrun, tags=tags)
        if result != 0:
            raise Exception("Problem building image: {imm}".format(imm=image['image']))


def make_image(image, dryrun=False, tags=[]):
    current_dir = os.getcwd()
    returnCode = -1
    try:
        docker_path = image['dockerfile']
        folder = os.path.dirname(docker_path)
        os.chdir(folder)
        tagsLine = ' '.join(['-t {imm}:{tag}'.format(imm=image["image"], tag=tag) for tag in tags])
        returnCode, _ = run('docker build --no-cache {tagsLine} -t {imm}:latest .'.format(imm=image["image"], tagsLine=tagsLine), dry=dryrun)
    finally:
        os.chdir(current_dir)

    return returnCode


if __name__ == '__main__':
    images = get_all_images("D:/swarm/images")

    print([x['image'] for x in get_build_image_chain(images, 'jmulla/rsm')])
    print([x['image'] for x in get_build_image_chain(images, 'jmulla/rsm', 'jmulla/ds-py')])

    images = get_build_image_chain(images, 'jmulla/rsm', 'jmulla/base')
    make_images(images)
