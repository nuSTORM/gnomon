from distutils.core import setup

def parse_requirements(file_name):
    requirements = []
    for line in open(file_name, 'r').read().split('\n'):
        if re.match(r'(\s*#)|(\s*$)', line):
            continue
        if re.match(r'\s*-e\s+', line):
            requirements.append(re.sub(r'\s*-e\s+.*#egg=(.*)$', r'\1', line))
        elif re.match(r'\s*-f\s+', line):
            pass
        else:
            requirements.append(line)

    return requirements

setup(
    name='gnomon',
    version='v0.1',
    packages=['gnomon', 'gnomon.processors'],
    url='https://github.com/nuSTORM/gnomon',
    license='LICENSE.txt',
    author='tunnell',
    author_email='c.tunnell1@physics.ox.ac.uk',
    description='',
    requires = parse_requirements('requirements.txt')
)
