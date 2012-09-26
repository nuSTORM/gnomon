from distutils.core import setup

def parse_requirements(file_name):
    requirements = []
    for line in open(file_name, 'r').readlines():
        requirements.append(line.rstrip('\n'))

    print requirements
    return requirements


def get_version():
    file_obj = open('VERSION')
    return file_obj.read().rstrip('\n')

setup(
    name='gnomon',
    version=get_version(),
    packages=['gnomon', 'gnomon.processors'],
    url='https://github.com/nuSTORM/gnomon',
    license='LICENSE.txt',
    author='Christopher Tunnell et.al.',
    maintainers='nuSTORM Far Detector Lead Developers',
    maintainers_email='tbd',
    author_email='c.tunnell1@physics.ox.ac.uk',
    long_description=open('README.rst').read(),
    description='desc',
    install_requires=parse_requirements('requirements.txt')
)
