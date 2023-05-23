import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as fr:
    install_requires = fr.read().splitlines()

with open("requirements-dev.txt") as fr:
    extra_require = {" dev": fr.read().splitlines()}

setuptools.setup(
    name="PyAutoAPI",
    version="0.0.3a1",
    description="Easily and automatically turn a database into an API",
    author="jay3ss",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jay3ss/pyautoapi",
    packages=setuptools.find_packages(),
    package_dir={
        "tests" : "tests",
        "pyautoapi": "pyautoapi",
        "examples": "examples",
    },
    package_data={
        "tests" : ["tests/data/*.sql"],
        "examples": ["tests/data/*.sql"],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: FastAPI",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.10",
    install_requires=install_requires,
    extra_require=extra_require,
    keywords=["PyAutoAPI", "FastAPI", "SQLAlchemy",],
)
