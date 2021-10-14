from distutils.core import setup
import sys

setup(name='pyshop',
      version='14.0.2.1',
      author='SINTEF Energy Research',
      description='Python interface to SHOP.',
      packages=['pyshop',
                'pyshop.helpers',
                'pyshop.shopcore'],
      package_dir={'pyshop': 'pyshop',
                   'pyshop.helpers': 'pyshop/helpers',
                   'pyshop.shopcore': 'pyshop/shopcore'},
      url='http://www.sintef.no/programvare/SHOP',
      author_email='support.energy@sintef.no',
      license='Commercial',
      install_requires=['matplotlib', 'pandas', 'numpy', 'graphviz', 'pybind11'])
