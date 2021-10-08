import pandas as pd
import matplotlib.pyplot as plt

from pyshop import ShopSession

license_path = r''
shop = ShopSession(license_path='', silent=False)

# Set time resolution
starttime = pd.Timestamp('2018-02-27')
endtime = pd.Timestamp('2018-02-28')
shop.set_time_resolution(starttime=starttime, endtime=endtime, timeunit='hour')

# Add scenarios
n_scen = 12
for i in range(1, n_scen + 1):
    scen_name = 'S' + str(i)
    if i > 1:
        scen = shop.model.scenario.add_object(scen_name)
    else:
        scen = shop.model.scenario[scen_name]
    scen.scenario_id.set(i)
    scen.probability.set(1.0/n_scen)
    scen.common_scenario.set(pd.Series([1, i], index=[starttime, starttime + pd.Timedelta(hours=1)]))

# Add topology
rsv1 = shop.model.reservoir.add_object('Reservoir1')
rsv1.max_vol.set(12)
rsv1.lrl.set(90)
rsv1.hrl.set(100)
rsv1.vol_head.set(dict(xy=[[0, 90], [12, 100], [14, 101]], ref=0))
rsv1.flow_descr.set(dict(xy=[[100, 0], [101, 1000]], ref=0))

plant1 = shop.model.plant.add_object('Plant1')
plant1.outlet_line.set(40)
plant1.main_loss.set([0.0002])
plant1.penstock_loss.set([0.0001])

p1g1 = shop.model.generator.add_object('Plant1_G1')
plant1.connect().generator.Plant1_G1.add()
p1g1.penstock.set(1)
p1g1.p_min.set(25)
p1g1.p_max.set(100)
p1g1.p_nom.set(100)
p1g1.startcost.set(500)
p1g1.gen_eff_curve.set(pd.Series([95, 98], index=[0, 100]))
# p1g1.gen_eff_curve.set(dict(xy=[[0, 95], [100, 98]], ref=0))  # Alternative way to set eff curve
p1g1.turb_eff_curves.set([pd.Series([80, 95, 90], index=[25, 90, 100], name=90),
                          pd.Series([82, 98, 92], index=[25, 90, 100], name=100)])
# p1g1.turb_eff_curves.set([dict(ref=90, xy=[[25, 80], [90, 95], [100, 90]]),
#                           dict(ref=100, xy=[[25, 82], [90, 98], [100, 92]])])  # Alternative way to set curve

rsv2 = shop.model.reservoir.add_object('Reservoir2')
rsv2.max_vol.set(5)
rsv2.lrl.set(40)
rsv2.hrl.set(50)
rsv2.vol_head.set(pd.Series([40, 50, 51], index=[0, 5, 6]))
# rsv2.vol_head.set(dict(xy=[[0, 40], [5, 50], [6, 51]], ref=0))
rsv2.flow_descr.set(pd.Series([0, 1000], index=[50, 51]))
# rsv2.flow_descr.set(dict(xy=[[50, 0], [51, 1000]], ref=0))

plant2 = shop.model.plant.add_object('Plant2')
plant2.outlet_line.set(0)
plant2.main_loss.set([0.0002])
plant2.penstock_loss.set([0.0001])

p2g1 = shop.model.generator.add_object('Plant2_G1')
plant2.connect().generator.Plant2_G1.add()
p2g1.penstock.set(1)
p2g1.p_min.set(25)
p2g1.p_max.set(100)
p2g1.p_nom.set(100)
p2g1.startcost.set(500)
p2g1.gen_eff_curve.set(pd.Series([95, 98], index=[0, 100]))
p2g1.turb_eff_curves.set([pd.Series([80, 95, 90], index=[25, 90, 100], name=90),
                          pd.Series([82, 98, 92], index=[25, 90, 100], name=100)])


# Connect objects
rsv1.connect().plant.Plant1.add()
plant1.connect().reservoir.Reservoir2.add()
rsv2.connect().plant.Plant2.add()

rsv1.start_head.set(92)
rsv2.start_head.set(43)
rsv1.energy_value_input.set(39.7)
rsv2.energy_value_input.set(38.6)

shop.model.market.add_object('Day_ahead')
da = shop.model.market.Day_ahead
da.sale_price.set(pd.DataFrame({'1': [39, 38.5],
                                '2': [39, 39.0],
                                '3': [39, 39.5],
                                '4': [39, 40],
                                '5': [39, 38.5],
                                '6': [39, 39.0],
                                '7': [39, 39.5],
                                '8': [39, 40],
                                '9': [39, 38.5],
                                '10': [39, 39.0],
                                '11': [39, 39.5],
                                '12': [39, 40]
                                }, index=[starttime, starttime + pd.Timedelta(hours=1)],
                               columns=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']))
da.buy_price.set(40.01)
da.max_buy.set(9999)
da.max_sale.set(9999)

rsv1.inflow.set(pd.DataFrame({'1': [101, 50],
                              '2': [101, 50],
                              '3': [101, 50],
                              '4': [101, 50],
                              '5': [101, 100],
                              '6': [101, 100],
                              '7': [101, 100],
                              '8': [101, 100],
                              '9': [101, 150],
                              '10': [101, 150],
                              '11': [101, 150],
                              '12': [101, 150]
                              }, index=[starttime, starttime + pd.Timedelta(hours=1)],
                             columns=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']))

shop.print_model([], ['full_1.lp'])
shop.start_sim([], ['1'])

shop.set_code(['incremental'], [])
shop.start_sim([], ['3'])

prod = shop.model.market.Day_ahead.sale_price.get()
prod.plot()
plt.title('Sale price')
prod = shop.model.reservoir.Reservoir1.inflow.get()
prod.plot()
plt.title('Reservoir 1 inflow')
prod = shop.model.plant.Plant1.production.get()
prod.plot()
plt.title('Production plant 1')
prod = shop.model.plant.Plant2.production.get()
prod.plot()
plt.title('Production plant 2')
prod = shop.model.reservoir.Reservoir1.storage.get()
prod.plot()
plt.title('Reservoir storage 1')
prod = shop.model.reservoir.Reservoir2.storage.get()
prod.plot()
plt.title('Reservoir storage 2')
plt.show()
