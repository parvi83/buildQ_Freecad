from setuptools import setup
import os

version_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                            "freecad", "buildQ_module", "version.py")
with open(version_path) as fp:
    exec(fp.read())

setup(name='freecad.buildQ_module',
      version=str(__version__),
      packages=['freecad',
                'freecad.buildQ_module'],
      maintainer="Paul Jarvis",
      maintainer_email="paul@prgoressivbuilding.com.au",
      url="https://foobar.com/me/coolWB",
      description="This workbench is for creating building elements for construction",
      install_requires=['numpy',],
      include_package_data=True)
