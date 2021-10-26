from distutils.core import setup
import sys
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(name='sintef-pyshop',
      version='1.0.0.dev3',
      author='SINTEF Energy Research',
      description='Python interface to SHOP',
      long_description=long_description,
      long_description_content_type='text/markdown',
      packages=['pyshop',
                'pyshop.helpers',
                'pyshop.shopcore'],
      package_dir={'pyshop': 'pyshop',
                   'pyshop.helpers': 'pyshop/helpers',
                   'pyshop.shopcore': 'pyshop/shopcore'},
      url='http://www.sintef.no/programvare/SHOP',
      project_urls={
          'Documentation': 'https://shop.sintef.energy/documentation/tutorials/pyshop/',
          'Source': 'https://github.com/sintef-energy/pyshop',
          'Tracker': 'https://shop.sintef.energy/tickets',
      },
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: MIT License',
          'Intended Audience :: Developers',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Education',
          'Intended Audience :: Science/Research',
          'Topic :: Scientific/Engineering',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
      ],
      author_email='support.energy@sintef.no',
      license='Commercial',
      python_requires='>=3.7, <3.9',
      install_requires=['matplotlib', 'pandas', 'numpy', 'graphviz', 'pybind11'])
