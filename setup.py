from setuptools import setup, find_packages

setup(
    name="pyro",
    version="0.1",
    author="fenish",
    author_email="sohretalhadev@gmail.com",
    description="A new UI Project for python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/fenish/pyro",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "flask",
        "flask_cors",
        "flask_socketio",
        "flask_compress",
        "python-dotenv",
        "transcrypt",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
