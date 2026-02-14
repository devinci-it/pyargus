"""
Setup configuration for PyArgus - SSH Bastion Application.

This file defines package metadata, dependencies, and installation instructions.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the long description from README if available
try:
    long_description = Path("wiki/pyargus/README.md").read_text(encoding="utf-8")
except FileNotFoundError:
    long_description = "PyArgus - SSH Bastion Application for secure server management"

setup(
    name="pyargus",
    version="0.1.0",
    author="devinci-it",
    author_email="vince.dev@icloud.com",
    description="SSH Bastion Application for secure server management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/devinci-it/pyargus",
    package_dir={"": "src"},
    packages=find_packages(where="src", exclude=["tests", "migrations", "scripts", "wiki"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.9",
    install_requires=[
        # Web Framework
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "pydantic==2.5.0",
        "pydantic-settings==2.1.0",
        # Database ORM
        "peewee==3.17.0",
        # SSH Management
        "paramiko==3.4.0",
        # Encryption
        "pycryptodome==3.19.0",
        # Environment Variables
        "python-dotenv==1.0.0",
        # Utilities
        "python-dateutil==2.8.2",
    ],
    extras_require={
        "dev": [
            "black==23.12.0",
            "flake8==6.1.0",
            "mypy==1.7.1",
            "isort==5.13.2",
            "httpx==0.25.2",
            "faker==21.0.0",
        ],
        "all": [
            "black==23.12.0",
            "flake8==6.1.0",
            "mypy==1.7.1",
            "isort==5.13.2",
            "httpx==0.25.2",
            "faker==21.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pyargus=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
