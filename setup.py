import setuptools


def get_requirements(file: str):
    with open(file, encoding='utf-8') as f:
        return f.read().splitlines()


def get_version(file: str):
    with open(file, encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip("'")
    raise RuntimeError('Unable to find version string.')


setuptools.setup(
    name='torchmenu',
    version=get_version('torchmenu/__version__.py'),
    description='TorchServe GUI',
    long_description=open('README.md').read(),
    python_requires='>=3.10',
    packages=setuptools.find_packages(exclude=['test', 'docs']),
    install_requires=get_requirements('requirements.txt'),
    include_package_data=True,
    extras_require={
        'dev': get_requirements('requirements-dev.txt'),
    },
    entry_points={
        'console_scripts': [
            'torchmenu = torchmenu.cli:main',
        ],
    },
)
