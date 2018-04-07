import sys
from setuptools import setup, find_packages

with open("VERSION") as f:
    version = f.read().strip()

setup_args = dict(
    name="drift-server-pages",
    version=version,
    author="Directive Games North",
    author_email="info@directivegames.com",
    description="Drift Server Pages",
    url="https://admin.drift-base.directivegames.com/",
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"]
    ),
    include_package_data=True,
)


if __name__ == "__main__":
    if {'upload', 'sdist'} & set(sys.argv):
        import driftserverpages
        try:
            driftserverpages.__version__.verify(setup_args['version'])
        except Exception as e:
            print "Warning!"
            print e

    setup(**setup_args)
