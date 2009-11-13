from setuptools import setup, find_packages

setup(name="django-twitter-oauth",
           version="0.1",
           description="Django application supporting twitter oauth and API",
           author="Brian Guertin",
           author_email="dev@brianguertin.com",
           packages=find_packages(),
           include_package_data=True,
)

