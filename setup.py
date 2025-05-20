from setuptools import setup, find_packages

setup(
    name="relay_control_app",
    version="0.1.0",
    description="Web-based relay control for 2-channel RS-232 module",
    packages=find_packages(),
    install_requires=[
        "Flask>=2.0",
        "pyserial>=3.4",
        "python-dotenv>=0.19",
    ],
    entry_points={
        "console_scripts": [
            # Starts the Flask app via `relay-web` command
            "relay-web=app:main",
        ],
    },
)
