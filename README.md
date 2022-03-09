# pyshop
Status:
[![codecov](https://codecov.io/gh/sintef-energy/pyshop/branch/main/graph/badge.svg?token=FYASF5O90D)](https://codecov.io/gh/sintef-energy/pyshop/branch/main/)

The nicest python interface to SHOP!

SHOP (Short-term Hydro Operation Planning) is a modeling tool for short-term hydro operation planning developed by SINTEF Energy Research in Trondheim, Norway. SHOP is used for both scientific and commerical purposes, please visit the [SHOP home page](https://www.sintef.no/en/software/shop/) for further information and inquiries regarding access and use.

The pyshop package is an open source python wrapper for SHOP, and requires the proper SHOP binaries to function (see step 2).

## 1 Installing pyshop
The pyshop package can be installed using pip, the package installer for python. Please visit the [pip home page](https://pip.pypa.io/en/stable/) for installation and any pip related issues. You can install the official pyshop release through the terminal command:

`pip install sintef-pyshop`

You can also clone this repository and install the latest development version. To do this, open a terminal in the cloned pyshop directory and give the command:

`pip install .`

You should now see pyshop appear in the list of installed python modules when typing:

`pip list`

## 2 Download the desired SHOP binaries for your system 

> NOTE: You may not distribute the cplex library as it requires end user license

The SHOP core is separate from the pyshop package, and must be downloaded separately. The latest SHOP binaries are found on the [SHOP Portal](https://shop.sintef.energy/files/). Access to the portal must be granted by SINTEF Energy Research.

The following binaries are required for pyshop to run:

Windows:
- cplex2010.dll
- shop_cplex_interface.dll
- shop_pybind.pyd

Linux:
- libcplex2010.so
- shop_cplex_interface.so
- shop_pybind.so

The solver specific binary is listed as cplex2010 here, but will change as new CPLEX versions become available. It is also possible to use the GUROBI and OSI solvers with SHOP. Note that the shop_cplex_interface.so used to contain the CPLEX binaries in the Linux distribution before SHOP version 14.3, and so older SHOP versions do not require the separate libcplex2010.so file.

## 3 Environment and license file

The SHOP license file, `SHOP_license.dat`, must always be located in the directory specified by the environment variable `ICC_COMMAND_PATH`. The `ICC_COMMAND_PATH` can be added as a persistent environment variable in the regular ways, or it can be set by pyshop on a session basis. If the keyword argument `license_path` is specified when creating an instance of the ShopSession class (see step 4), the environment variable is overridden in the local environment of the executing process. If SHOP complains about not finding the license file, it is likely an issue with the `ICC_COMMAND_PATH` not being correctly specified.

The `ICC_COMMAND_PATH` is also the default place pyshop will look for the SHOP binaries mentioned in step 2. If the binaries are placed elsewhere, the keyword argument `solver_path` must be used when a ShopSession instance is created to ensure the correct binaries are loaded. Note that libcplex2010.so must be placed in the '/lib' directory when running pyshop in a Linux environment.

## 4 Running SHOP

Now that pyshop is installed, the SHOP binaries are downloaded, and the license file and binary paths are located, it is possible to run SHOP in python using pyshop:

    import pyshop as pys
    
    shop = pys.ShopSession(license_path="C:/License/File/Path", solver_path="C:/SHOP/versions/14")
    
    #Set time resolution
    #Build topolgy
    #Add temporal input
    #Run model
    #Retreive results

Please visit the SHOP Portal for a detailed [tutorial](https://shop.sintef.energy/documentation/tutorials/pyshop/) and several [examples](https://shop.sintef.energy/documentation/examples/) using pyshop.
