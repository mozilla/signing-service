from setuptools import setup, find_packages


setup(name='signing_service',
      version='0.1',
      description="Mozilla's Marketplace receipt, FirefoxOS app, "
                  "and addons signing service",
      long_description='',
      author='Ryan Tilder and contributors',
      author_email='services-dev@mozilla.com',
      license='MPL 2.0 (Mozilla Public License)',
      url='https://github.com/mozilla/signing_service',
      include_package_data=True,
      classifiers=[],
      packages=find_packages(exclude=['tests']),
      # NOTE: you must use pip to install all dependencies.
      install_requires=[])
