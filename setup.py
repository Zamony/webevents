from setuptools import setup, find_packages

def read_readme():
    readme_text = None
    with open("README.md") as readme:
        readme_text = readme.read()
    return readme_text

setup(
    name="webevents",
    version="0.1.4",
    packages=["webevents"],
    package_data={
        "webevents": ["webevents.js"],
    },
    author="Nikita Mochalov",
    author_email="mochalov.n@ya.ru",
    description="A little Python library for making simple HTML/JS GUI apps",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url='https://github.com/Zamony/webevents',
    license="MIT",
    keywords="gui html js events eel electron",
    install_requires=[],
    python_requires="~=3.6"
)
