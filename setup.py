from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README_EN.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements from requirements.txt
with open('requirements.txt') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="obs-complete-assistant",
    version="1.0.0",
    author="OBS Assistant Team",
    author_email="contact@obsassistant.com",
    description="A comprehensive assistant for OBS Virtual Camera with OCR and audio processing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/obs-assistant/obs-complete-assistant",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Video :: Capture",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=6.0',
            'black>=21.0',
            'flake8>=3.8',
            'mypy>=0.910',
        ],
    },
    entry_points={
        'console_scripts': [
            'obs-assistant=obs_assistant:main',
        ],
    },
    include_package_data=True,
    package_data={
        '': ['*.md', '*.txt', '*.json', '*.env.example'],
    },
    keywords="obs virtual-camera ocr speech-to-text openai gpt-4 interview-assistant",
    project_urls={
        "Bug Reports": "https://github.com/obs-assistant/obs-complete-assistant/issues",
        "Source": "https://github.com/obs-assistant/obs-complete-assistant",
        "Documentation": "https://github.com/obs-assistant/obs-complete-assistant#readme",
        "Changelog": "https://github.com/obs-assistant/obs-complete-assistant/blob/main/CHANGELOG.md",
        "Security": "https://github.com/obs-assistant/obs-complete-assistant/blob/main/SECURITY.md",
    },
)