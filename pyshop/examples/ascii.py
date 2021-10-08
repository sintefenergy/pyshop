import matplotlib.pyplot as plt

from pyshop import ShopSession

# Create a new SHOP session.
shop = ShopSession(license_path='', silent=False)

shop.read_ascii_file('test_time.ascii')
shop.read_ascii_file('test_model.ascii')
shop.read_ascii_file('test_data.ascii')

shop.run_command_file('.', 'py_test_commands.txt')

plt.title('Production and price')
plt.xlabel('Time')
plt.ylabel('Production [MW]')

ax = shop.model.market['1'].sale_price.get().plot(legend='Price', secondary_y=True)
shop.model.plant.Plant1.production.get().plot(legend='Plant 1')
shop.model.plant.Plant2.production.get().plot(legend='Plant 2')
ax.set_ylabel('Price [NOK]')
plt.show()

plt.figure(2)
prod = shop.model.reservoir.Reservoir1.inflow.get()
prod.plot()

prod = shop.model.reservoir.Reservoir1.storage.get()
prod.plot()

prod = shop.model.reservoir.Reservoir2.storage.get()
prod.plot()
