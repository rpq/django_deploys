import glob
from distutils.core import setup

with open('PYPI_CLASSIFIERS.txt') as f:
    PYPI_CLASSIFIERS = filter(None, f.read().split('\n'))
with open('REQUIREMENTS.txt') as f:
    REQUIREMENTS = filter(None, f.read().split('\n'))
with open('README.md') as f:
    README = f.read()

data_files = ['MIT_LICENSE.txt', 'REQUIREMENTS.txt', 'README.md',
    'PYPI_CLASSIFIERS.txt',]
data_files.extend(glob.glob('templates/*'))

script_files = glob.glob('src/scripts/*')

setup(
    name='django_deploys',
    version='0.1.10',
    url='https://github.com/rpq/django_deploys',

    data_files=[
        ('django_deploys', data_files),],
    scripts=script_files,

    description='Some django deploy fabric methods',
    install_requires=REQUIREMENTS,
    long_description=README,
    license='MIT_LICENSE.txt',
    classifiers=PYPI_CLASSIFIERS,

    author='Ramon Paul Quezada',
    author_email='rpq@winscores.com',
)
