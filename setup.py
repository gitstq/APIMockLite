"""
Setup script for APIMockLite
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    requirements = [
        line.strip()
        for line in requirements_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="apimocklite",
    version="1.0.0",
    author="gitstq",
    author_email="",
    description="🚀 APIMockLite - Lightweight AI-Powered API Mock Server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gitstq/APIMockLite",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing :: Mocking",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "yaml": ["PyYAML>=6.0"],
        "dev": ["pytest>=7.0", "black", "flake8", "mypy"],
    },
    entry_points={
        "console_scripts": [
            "apimocklite=apimocklite.cli:main",
            "apiml=apimocklite.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "api",
        "mock",
        "server",
        "testing",
        "development",
        "http",
        "rest",
        "ai",
        "cli",
    ],
    project_urls={
        "Bug Reports": "https://github.com/gitstq/APIMockLite/issues",
        "Source": "https://github.com/gitstq/APIMockLite",
        "Documentation": "https://github.com/gitstq/APIMockLite#readme",
    },
)
