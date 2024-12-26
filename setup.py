"""Setup script for the Hawkins Agent Framework"""

from setuptools import setup, find_packages

with open("docs/README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="hawkins-agent",
    version="0.1.0",
    author="Harish Santhanalakshmi Ganesan",
    description="A Python SDK for building AI agents with minimal code using Hawkins ecosystem with HawkinDB memory",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hawkins-ai/hawkins-agent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.11",
    install_requires=[
        "aiohttp>=3.8.0",
        "build>=1.2.2.post1",
        "flask[async]>=3.1.0",
        "google-api-python-client>=2.156.0",
        "hatchling>=1.27.0",
        "hawkins-rag>=0.1.0",
        "hawkinsdb>=1.0.1",
        "litellm>=1.0.0",
        "openai>=1.58.1",
        "python-dotenv>=0.19.0",
        "serpapi>=0.1.5",
        "tavily-python>=0.5.0",
        "trafilatura>=2.0.0",
        "twine>=6.0.1",
        "wheel>=0.45.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "mypy>=1.0.0"
        ],
        "full": [
            "build>=1.2.2.post1",
            "wheel>=0.45.1",
        ]
    },
)
