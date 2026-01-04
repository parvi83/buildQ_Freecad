from setuptools import setup
import os

version_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                            "freecad", "buildQ", "version.py")
with open(version_path) as fp:
    exec(fp.read())

setup(name='freecad.buildQ',
      version=str(__version__),
      packages=['freecad',
                'freecad.buildQ'],
      maintainer="Paul Jarvis",
      maintainer_email="paul@prgoressivbuilding.com.au",
      url="",
      description="This workbench is for creating building elements for construction",
      install_requires=['numpy',],
      include_package_data=True)
