from setuptools import setup, find_packages

setup(
    name="vr_automation",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "streamlit",
        "openpyxl",
        "pydantic",
        "pydantic-settings",
        "plotly",
        "python-dotenv",
        "numpy",
        "python-dateutil"
    ]
)
