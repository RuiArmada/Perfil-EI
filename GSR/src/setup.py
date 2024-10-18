from setuptools import setup, find_packages

setup(
    name='domotics',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        # Add other dependencies here if needed
    ],
    entry_points={
        'console_scripts': [
            'run_domotics=domotics.run_applications:main',
        ],
    },
    include_package_data=True,
    package_data={
        'domotics': ['mib.json'],
    },
)
