import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cascade-ui",
    version="0.1.1",
    author="Oleg Sevostyanov,Ilia Moiseev",
    author_email="ilia.moiseev.5@yandex.ru",
    license="Apache License 2.0",
    description="Web-UI for Cascade - Lightweight and modular MLOps library targeted at small teams or individuals ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/laiserk/cascade_ui",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    package_dir={"cascade_ui": "cascade_ui"},
    include_package_data=True,
    package_data={"cascade_ui": ["web/dist/**"]},
    packages=setuptools.find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "cascade-ml>=0.16.0",
        "fastapi>=0.110.0",
        "uvicorn>=0.29.0",
        "pydantic>=2.6.4",
    ],
)
