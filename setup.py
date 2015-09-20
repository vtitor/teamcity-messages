# coding=utf-8
from setuptools import setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        import sys

        if not self.pytest_args:
            self.pytest_args = ["-l", "--junitxml=test-result.xml", "tests/unit-tests", "tests/integration-tests"]
            if sys.version_info >= (2, 6):
                self.pytest_args.append("tests/unit-tests-since-2.6")

        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

setup(
    name="teamcity-messages",
    version="1.16",
    author='JetBrains',
    author_email='teamcity-feedback@jetbrains.com',
    description='Send test results ' +
                'to TeamCity continuous integration server from unittest, nose, py.test, twisted trial (Python 2.4+)',
    long_description="""This packages provides unittest, nose, py.test, twisted trial
plugins for sending test result messages
to TeamCity continuous integration server
http://www.jetbrains.com/teamcity/

**unittest**: see examples/simple.py for example how to
write your own test file which reports messages
under TeamCity and prints usual diagnostics without it.

**nose**, **py.test** : test status reporting enabled automatically under TeamCity build (when teamcity-messages package is installed)

**django**: For Django 1.6+: Use the Teamcity runner instead of the default DiscoverRunner by changing the following setting in your settings.py:
TEST_RUNNER = "teamcity.django.TeamcityDjangoRunner"
If you are using another test runner, you should override the `run_suite` method or use the `DiscoverRunner.test_runner` property introduced in Django 1.7.

**flake8**: add `--teamcity` option to flake8 command line to report errors and warning as TeamCity failed tests

**twisted trial**: add `--reporter=teamcity` option to trial command line

ChangeLog: https://github.com/JetBrains/teamcity-messages/blob/master/CHANGELOG.txt

Issue Tracker: https://github.com/JetBrains/teamcity-messages/issues
""",
    license='Apache 2.0',
    keywords='unittest teamcity test nose py.test pytest jetbrains',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.4',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Testing'
    ],
    url="https://github.com/JetBrains/teamcity-messages",
    platforms=["any"],

    packages=["teamcity", "twisted.plugins"],
    zip_safe=False,
    package_data={
        'twisted': ['plugins/teamcity_plugin.py'],
    },

    tests_require=['pytest', 'virtualenv'],
    cmdclass={'test': PyTest},

    entry_points={
        'nose.plugins.0.10': [
            'teamcity-report = teamcity.nose_report:TeamcityReport'
        ],

        'pytest11': [
            'pytest-teamcity = teamcity.pytest_plugin',
        ],

        'flake8.extension': [
            'P999 = teamcity.flake8_plugin',
        ]
    },
)

# Make Twisted regenerate the dropin.cache, if possible.  This is necessary
# because in a site-wide install, dropin.cache cannot be rewritten by
# normal users.
#
# See https://stackoverflow.com/questions/7275295/how-do-i-write-a-setup-py-for-a-twistd-twisted-plugin-that-works-with-setuptools
# to discover deepness of this pit.
try:
    from twisted.plugin import IPlugin, getPlugins
    from twisted.python import log

    def my_log_observer(d):
        if d.get("isError", 0):
            import sys

            text = log.textFromEventDict(d)
            sys.stderr.write("\nUnhandled error while refreshing twisted plugins cache: \n")
            sys.stderr.write("    " + text.replace("\n", "\n    "))
    log.startLoggingWithObserver(my_log_observer, setStdout=False)

    list(getPlugins(IPlugin))
except:
    # Do not break module install because of twisted internals
    pass
