from setuptools import setup

setup(
    name='django-model-values',
    version='1.0',
    description='Taking the O out of ORM.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Aric Coady',
    author_email='aric.coady@gmail.com',
    url='https://github.com/coady/django-model-values',
    project_urls={'Documentation': 'https://django-model-values.readthedocs.io'},
    license='Apache Software License',
    py_modules=['model_values'],
    install_requires=['django>=1.11', 'six'],
    python_requires='>=2.7',
    tests_require=['pytest-django', 'pytest-cov'],
    keywords='values_list pandas column-oriented data mapper pattern orm',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Database :: Database Engines/Servers',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
