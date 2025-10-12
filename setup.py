from setuptools import setup, find_packages

setup(
    name="job-application-automation",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'requests',
        'beautifulsoup4',
        'python-docx',
        'openai',
        'pypdf',
        'flask',
        'python-dotenv',
        'docx2pdf',
        'reportlab',
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'jobapp-diag=src.helper.cli:main',
        ],
    },
)