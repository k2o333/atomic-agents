from setuptools import setup, find_packages

setup(
    name="interfaces",
    version="0.1.0",
    author="Synapse Team",
    description="Core data contracts for the Synapse platform",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
    ],
    python_requires=">=3.11",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.11",
    ],
)