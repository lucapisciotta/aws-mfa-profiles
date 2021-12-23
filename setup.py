from pathlib import Path
from setuptools import setup

# The directory containing this file
HERE = Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()


setup(
    name='aws-mfa-profiles',
    version='1.1.0',
    description='A package to create credential for AWS using MFA and with the support of multiple profiles',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/lucapisciotta/aws-mfa-profiles',
    author='Luca Pisciotta',
    author_email='luca.pisciotta+pypi@live.it',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Development Status :: 5 - Production/Stable'
    ],
    packages=['aws_mfa_profiles'],
    include_package_data=True,
    install_requires=['boto3'],
    entry_points={
        'console_scripts': [
            'aws-mfa-profiles=aws_mfa_profiles.__main__:main',
            ],
        }
)
