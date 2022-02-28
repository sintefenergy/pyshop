import pandas as pd
import matplotlib.pyplot as plt

from pyshop import ShopSession

# Create a new SHOP session.
shop = ShopSession(license_path='', silent=False, log_file='')

# Set time resolution
starttime = pd.Timestamp('2018-02-27')
endtime = pd.Timestamp('2018-02-28')
shop.set_time_resolution(starttime=starttime, endtime=endtime, timeunit='hour')

# Add objects
rsv1 = shop.model.reservoir.add_object('Reservoir1')
rsv1.max_vol.set(12)
rsv1.lrl.set(90)
rsv1.hrl.set(100)
rsv1.vol_head.set(pd.Series([90, 100, 101], index=[0, 12, 14], name=0))
rsv1.flow_descr.set(pd.Series([0, 1000], index=[100, 101], name=0))

rsv2 = shop.model.reservoir.add_object('Reservoir2')
rsv2.max_vol.set(5)
rsv2.lrl.set(90)
rsv2.hrl.set(100)
rsv2.vol_head.set(pd.Series([90, 100, 101], index=[0, 5, 6]))
rsv2.flow_descr.set(pd.Series([0, 1000], index=[100, 101]))

junc1 = shop.model.junction.add_object('Junction1')
junc1.loss_factor_1.set(0.00015)
junc1.loss_factor_2.set(0.00030)

plant1 = shop.model.plant.add_object('Plant1')
plant1.outlet_line.set(40)
plant1.main_loss.set([0.0002])
plant1.penstock_loss.set([0.0001])

p1g1 = shop.model.generator.add_object('Plant1_G1')
plant1.connect_to(p1g1)
p1g1.penstock.set(1)
p1g1.p_min.set(25)
p1g1.p_max.set(100)
p1g1.p_nom.set(100)
p1g1.startcost.set(500)
p1g1.gen_eff_curve.set(pd.Series([95, 98], index=[0, 100]))
p1g1.turb_eff_curves.set([
    pd.Series([80, 95, 90], index=[25, 90, 100], name=90),
    pd.Series([82, 98, 92], index=[25, 90, 100], name=100)
])

junc2 = shop.model.junction.add_object('Junction2')
junc2.loss_factor_1.set(0.00020)
junc2.loss_factor_2.set(0.00050)

creek1 = shop.model.creek_intake.add_object('Creek1')
creek1.inflow.set(pd.DataFrame([20, 10, 5, 0], index=[starttime + pd.Timedelta(hours=i) for i in [0, 6, 12, 18]]))
creek1.max_inflow.set(80)
creek1.net_head.set(55)

rsv3 = shop.model.reservoir.add_object('Reservoir3')
rsv3.max_vol.set(5)
rsv3.lrl.set(40)
rsv3.hrl.set(50)
rsv3.vol_head.set(pd.Series([40, 50, 51], index=[0, 5, 6]))
rsv3.flow_descr.set(pd.Series([0, 1000], index=[50, 51]))

plant2 = shop.model.plant.add_object('Plant2')
plant2.outlet_line.set(0)
plant2.main_loss.set([0.0002])
plant2.penstock_loss.set([0.0001])

p2g1 = shop.model.generator.add_object('Plant2_G1')
plant2.connect_to(p2g1)
p2g1.penstock.set(1)
p2g1.p_min.set(25)
p2g1.p_max.set(100)
p2g1.p_nom.set(100)
p2g1.startcost.set(500)
p2g1.gen_eff_curve.set(pd.Series([95, 98], index=[0, 100]))
p2g1.turb_eff_curves.set([
    pd.Series([80, 95, 90], index=[25, 90, 100], name=90),
    pd.Series([82, 98, 92], index=[25, 90, 100], name=100)
])

# Connect objects
rsv1.connect_to(junc1)
rsv2.connect_to(junc1)
junc1.connect_to(plant1)
plant1.connect_to(rsv3)
rsv3.connect_to(junc2)
creek1.connect_to(junc2)
junc2.connect_to(plant2)

rsv1.start_head.set(92)
rsv2.start_head.set(92)
rsv3.start_head.set(43)
rsv1.energy_value_input.set(39.7)
rsv2.energy_value_input.set(39.7)
rsv3.energy_value_input.set(38.6)

shop.model.market.add_object('Day_ahead')
da = shop.model.market.Day_ahead
da.sale_price.set(39.99)
da.buy_price.set(40.01)
da.max_buy.set(9999)
da.max_sale.set(9999)

rsv1.inflow.set(pd.DataFrame([101, 50], index=[starttime, starttime + pd.Timedelta(hours=1)]))
rsv2.inflow.set(pd.DataFrame([10, 50], index=[starttime, starttime + pd.Timedelta(hours=1)]))
rsv3.inflow.set(pd.DataFrame([0, 20], index=[starttime, starttime + pd.Timedelta(hours=1)]))

for i in range(3):
    shop.print_model('','full{}.lp'.format(str(i + 1)))
    shop.start_sim('',1)
shop.set_code(['incremental'],[])
shop.start_sim('',3)

plt.title('Production and price')
plt.xlabel('Time')
plt.ylabel('Production [MW]')

ax = shop.model.market.Day_ahead.sale_price.get().plot(legend='Price', secondary_y=True)
shop.model.plant.Plant1.production.get().plot(legend='Plant 1')
shop.model.plant.Plant2.production.get().plot(legend='Plant 2')
ax.set_ylabel('Price [NOK]')
plt.show()

plt.figure(2)
plt.title('Storage and inflow')
plt.xlabel('Time')
plt.ylabel('Storage [Mm3]')
ax = shop.model.reservoir.Reservoir1.inflow.get().plot(legend='Inflow1', secondary_y=True)
shop.model.reservoir.Reservoir2.inflow.get().plot(legend='Inflow2', secondary_y=True)
shop.model.reservoir.Reservoir3.inflow.get().plot(legend='Inflow3', secondary_y=True)
shop.model.creek_intake['Creek1'].inflow.get().plot(legend='Creek1', secondary_y=True)
ax.set_ylabel('Flow [m3/s]')
shop.model.reservoir.Reservoir1.storage.get().plot(legend='Storage1')
shop.model.reservoir.Reservoir2.storage.get().plot(legend='Storage2')
shop.model.reservoir.Reservoir3.storage.get().plot(legend='Storage3')

plt.show()