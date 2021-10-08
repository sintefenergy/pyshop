# pyshop
The nicest python interface to SHOP
# 1 Place missing external libraries into *this* directory

> NOTE: You may not distribut cplex library as it requires end user license

You will find these under /shop/bin

Windows:
- cplex2010.dll
- shop_cplex_interface.dll
- shop_pybind.pyd

Linux:
- libcplex2010.so
- shop_cplex_interface.so
- shop_pybind.so

# Environment

Windows:

> `ICC_COMMAND_PATH` should be set to path where `SHOP_License.dat` can be found.

Linux:

> `ICC_COMMAND_PATH` should be set to path where `SHOP_License.dat` can be found, and additionally the `*.so` files listed in *step 1* must also be copied or moved to this location.

# 3 Install

`pip install .`