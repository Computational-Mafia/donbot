from setuptools import setup, find_packages

setup(
    name='donbot-python',
    version='0.1.0',
    description='a Python library for automating activities on mafiascum.net',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Computational-Mafia/donbot',
    author='Jordan Gunn',
    author_email='gunnjordanb@gmail.com',
    packages=find_packages(),
    install_requires=["lxml"],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    python_requires='>=3.7',
)
