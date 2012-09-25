from distutils.core import setup

def parse_requirements(file_name):
    requirements = []
    for line in open(file_name, 'r').readlines():
        requirements.append(line.rstrip('\n'))

    print requirements
    return requirements

setup(
    name='gnomon',
    version='v0.1',
    packages=['gnomon', 'gnomon.processors'],
    url='https://github.com/nuSTORM/gnomon',
    license='LICENSE.txt',
    author='tunnell',
    author_email='c.tunnell1@physics.ox.ac.uk',
    long_description=open('README.rst').read(),
    description='desc',
    install_requires = parse_requirements('requirements.txt')
)
