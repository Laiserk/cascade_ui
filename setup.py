import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cascade-ui",
    version="0.1.0",
    author="Oleg Sevostyanov,Ilia Moiseev",
    author_email="ilia.moiseev.5@yandex.ru",
    license="Apache License 2.0",
    description="Web-UI for Cascade - ML Engineering Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/laiserk/cascade_ui",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    package_dir={"cascade_ui": "./cascade_ui"},
    packages=setuptools.find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "cascade-ml>=0.12.0,<0.13"
    ],
)
