from setuptools import setup, find_packages

setup(
    name="LoggingService",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "opentelemetry-api",
        "opentelemetry-sdk",
        "python-json-logger",
    ],
    author="Synapse Team",
    description="Logging & Tracing Service for the Synapse platform",
)