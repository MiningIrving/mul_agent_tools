from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="mul_agent_tools",
    version="0.1.0",
    author="MiningIrving",
    author_email="",
    description="A state-driven multi-agent financial analysis framework using LangGraph",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MiningIrving/mul_agent_tools",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0", 
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.2.0",
        ],
        "data": [
            "yfinance>=0.2.0",
            "akshare>=1.9.0",
            "tushare>=1.3.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "mul-agent-tools=mul_agent_tools.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)