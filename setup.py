from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ai-compiler",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="An AI-powered compiler with modern features and extensible architecture",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ai-compiler",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Compilers",
    ],
    python_requires=">=3.8",
    install_requires=[
        "llvmlite>=0.40.0",
        "pyyaml>=6.0.1",
        "typing-extensions>=4.5.0",
        "flask>=2.3.3",
        "flask-cors>=4.0.0",
        "python-dotenv>=1.0.0",
        "openai>=1.3.0",
        "numpy>=1.24.3",
        "pandas>=2.0.3",
        "scikit-learn>=1.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "flake8>=6.1.0",
            "mypy>=1.5.1",
            "sphinx>=7.1.2",
            "sphinx-rtd-theme>=1.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ai-compiler=compiler.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "compiler": [
            "config/*.yaml",
            "templates/*",
            "static/*",
        ],
    },
) 