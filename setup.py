from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="eleven-layer-ai",
    version="1.1.0",
    author="Yingjie Gao",
    author_email="billgaohub@users.noreply.github.com",
    description="AIUCE - AI Universe Constitution Evolution System (十一层治理架构)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/billgaohub/aiuce",
    packages=find_packages(exclude=("tests", "tests.*")),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black>=23.0.0",
            "mypy>=1.5.0",
            "flake8>=6.0.0",
        ],
        "advanced": [
            "transformers>=4.30.0",
            "torch>=2.0.0",
            "chromadb>=0.4.0",
            "sentence-transformers>=2.2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "eleven-layer=eleven_layer_ai.cli:main",
        ],
    },
)
