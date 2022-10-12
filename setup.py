from setuptools import setup, find_packages

setup(
    name='assistot',
    version='1.1',
    packages=find_packages(),
    url='',
    license='MIT',
    author='Sumit Chachadi',
    author_email='sumitmal@buffalo.com',
    description='Personal Todo assistant',
    include_package_data=True,
    install_requires=[
        "Flask==2.1.2",
        "Flask-SQLAlchemy==2.5.1",
        "Flask-SQLAlchemy-Session==1.1",
        "PyMySQL==1.0.2",
        "requests==2.27.1",
        "setuptools==58.0.0",
        "SQLAlchemy==1.4.37",
        "cryptography==37.0.2",
        "Werkzeug==2.0.3",
        "pytest==7.1.2",
        "Flask-Migrate==3.1.0",
        "gunicorn==20.1.0"
    ]
)
