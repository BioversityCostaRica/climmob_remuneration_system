import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.md")) as f:
    README = f.read()
with open(os.path.join(here, "CHANGES.txt")) as f:
    CHANGES = f.read()

requires = ["climmob"]

tests_require = ["WebTest >= 1.3.1", "pytest", "pytest-cov"]

setup(
    name="RemunerationSystem",
    version="1.0",
    description="Remuneration system for assistants",
    long_description=README + "\n\n" + CHANGES,
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author="Carlos Quiros",
    author_email="c.f.quiros@cgiar.org",
    url="https://climmob.net",
    keywords="climmob plugin",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    extras_require={"testing": tests_require},
    install_requires=requires,
    entry_points={
        "climmob.plugins": [
            "RemunerationSystem = RemunerationSystem.plugin:RemunerationSystem"
        ]
    },
)
