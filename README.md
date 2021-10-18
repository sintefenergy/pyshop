# pyshop
The nicest python interface to SHOP!

## 1 Installing pyshop
The pyshop package can be installed using pip, the package installer for python: https://pip.pypa.io/en/stable/. Please make sure that you have installed pip and that it is found in your path. You can install the official pyshop release by opening a terminal and giving the following command:

`pip install sintef-pyshop`

You can also clone this repository and install the latest development version. To do this, open a terminal in the cloned pyshop directory and give the command:

`pip install .`

You should see pyshop appear in the list of installed python modules if you give the command:

`pip list`

## 2 Download the desired SHOP binaries for your system 

> NOTE: You may not distribute the cplex library as it requires end user license

The SHOP core is separate from the pyshop package, and must be downloaded separately. The latest SHOP binaries are found on the SHOP Portal under the "Files" tab: https://shop.sintef.energy/files/.

The following binaries are required for pyshop to run:

Windows:
- cplex2010.dll
- shop_cplex_interface.dll
- shop_pybind.pyd

Linux:
- cplex2010.so
- shop_cplex_interface.so
- shop_pybind.so

The solver specific binary is listed as cplex2010 here, but will change as new CPLEX versions become available. It is also possible to use the GUROBI and OSI solvers with SHOP.

## 3 Environment and license file

The SHOP license file, `SHOP_license.dat`, must always be located in the directory specified by the environment variable `ICC_COMMAND_PATH`. The `ICC_COMMAND_PATH` can be set by pyshop if the keyword argument `license_path` is specified when creating an instance of the ShopSession class (see step 4). The `ICC_COMMAND_PATH` is also the default place pyshop will look for the SHOP binaries mentioned in step 2. If the binaries are placed elsewhere, the keyword argument `solver_path` should be used when a ShopSession instance is created to override the default location. 

## 4 Running SHOP

Now that pyshop is installed, the SHOP binaries are downloaded, and the license file and binary paths are located, it is possible to run SHOP in python using pyshop:

    import pyshop as pys
    shop = pys.ShopSession(license_path="C:/My/License/File/Path", solver_path="C:/SHOP/versions/14.0.2.2")
    
    #Set time resolution
    #Build topolgy
    #Add temporal input
    #Run model
    #Retreive results

Please visit the SHOP Portal for detailed tutorials and examples using pyshop: https://shop.sintef.energy/documentation/.
