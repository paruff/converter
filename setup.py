"""Setup script for Media Converter.

This is for backwards compatibility. Modern installations should use pyproject.toml.
"""

from setuptools import setup, find_packages

setup(
    name="media-converter",
    version="0.1.0",
    description="A robust media conversion engine for repairing and encoding legacy video formats",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Media Converter Team",
    license="MIT",
    packages=find_packages(exclude=["tests*", "tmp_fix*", "originals*", "logs*"]),
    python_requires=">=3.10",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "ruff>=0.0.280",
            "mypy>=1.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "media-converter=cli:main",
            "media-converter-gui=gui:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Video :: Conversion",
    ],
)
