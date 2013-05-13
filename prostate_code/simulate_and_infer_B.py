import get_model_helper
import pdb
import matplotlib.pyplot as plt

data = get_model_helper.fake_data_getter().get_data(0.7, 0.7, 2.0, 1.0, 1.0, 1.0, 15.0, 15.0, 1)

pdb.set_trace()


fig = plt.figure()

ax = fig.add_subplot(2,2,1)

ax.scatter(data.X[0], data.obs['a'])
ax.set_title('a')

ax = fig.add_subplot(2,2,2)

ax.scatter(data.X[0], data.obs['b'])
ax.set_title('c')

ax = fig.add_subplot(2,2,3)

ax.scatter(data.X[0], data.obs['c'])
ax.set_title('c')

fig.show()

pdb.set_trace()
