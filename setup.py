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
      package_data={'pyshop': ['shop_pybind.pyd', 'shop_cplex_interface.dll', 'cplex2010.dll',
                               'shop_osi_interface.dll'] if sys.platform.startswith('win') else ['shop_pybind.so']},
      url='http://www.sintef.no/programvare/SHOP',
      author_email='support.energy@sintef.no',
      license='Commercial',
      install_requires=['matplotlib', 'pandas', 'numpy', 'graphviz', 'pybind11'])
