from setuptools import find_packages, setup

setup(
    name="lms",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "flask",
        "python-dotenv",
        "flask_sqlalchemy",
        "flask_cors",
        "SQLAlchemy",
        "mysql-connector-python",
        "requests",
        "werkzeug",
        "boto3",
        "pytz",
        "pytest"
    ],
)
