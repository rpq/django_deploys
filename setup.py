from distutils.core import setup

with open('PYPI_CLASSIFIERS.txt') as f:
    PYPI_CLASSIFIERS = filter(None, f.read().split('\n'))
with open('REQUIREMENTS.txt') as f:
    REQUIREMENTS = filter(None, f.read().split('\n'))
with open('README.md') as f:
    README = f.read()

setup(
    name='django_deploys',
    version='0.1.0',
    data_files=[('django_deploys',
        ['MIT_LICENSE.txt',
        'REQUIREMENTS.txt',
        'README.md',
        'PYPI_CLASSIFIERS.txt']),],
    install_requires=REQUIREMENTS,
    scripts=['src/scripts/django_deploys.py', 'src/scripts/django_deploys_fabfile.py'],

    description='Some django deploy fabric methods',
    long_description=README,
    license='MIT_LICENSE.txt',

    author='Ramon Paul Quezada',
    author_email='rpq@winscores.com',
    url='https://github.com/rpq/django_deploys',
    classifiers=PYPI_CLASSIFIERS,
)
