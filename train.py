from math import sqrt
from numpy import array2string
from numpy import concatenate
from matplotlib import pyplot
from pandas import DataFrame
from pandas import concat
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.callbacks import EarlyStopping
import argparse
from connectDB import ConnectDB
import time

class trainModel(object):
    SYMBOL = 0
    ID_COIN = 1
    def __init__(self, coin=None, n_hours=1, n_time_predicts=1, config_train=None, units=None):
        self.coin = coin
        self.n_hours = n_hours
        self.n_time_predicts = n_time_predicts
        self.config_train = config_train
        self.units = units
        self.db = ConnectDB()
        self.scaler = MinMaxScaler(feature_range=(0, 1))

    def series_to_supervised(self, data, n_in=1, n_out=1, dropnan=True):
        n_vars = 1 if type(data) is list else data.shape[1]
        df = DataFrame(data)
        cols, names = list(), list()
        for i in range(0, n_out):
            cols.append(df.shift(i))
            if i == 0:
                names += [('var%d(t)' % (j+1)) for j in range(n_vars)]
            else:
                names += [('var%d(t+%d)' % (j+1, i)) for j in range(n_vars)]
        for i in range(n_in, 0, -1):
            cols.append(df.shift(-i))
            names += [('var%d(t+%d)' % (j+1, i)) for j in range(n_vars)]
        agg = concat(cols, axis=1)
        agg.columns = names
        if dropnan:
            agg.dropna(inplace=True)
        agg = agg.fillna(0)
        return agg

    def build_model(self, units, train_X, loss='mse', optimizer='adam'):
        model = Sequential()
        model.add(LSTM(units,input_shape=(train_X.shape[1], train_X.shape[2]), return_sequences=True))
        model.add(LSTM(units))
        model.add(Dense(1))
        model.compile(loss=loss, optimizer=optimizer)
        return model

    def save_img_predict_test(self, inv_yhat, inv_y, symbol):
        pyplot.plot(inv_yhat, label='predict')
        pyplot.plot(inv_y, label='test')
        pyplot.legend()
        pyplot.savefig("img/chart_%s.png"%symbol)
        pyplot.close()

    def make_predict(self, model, test_X, n_hours = 1, n_features = 1):
        yhat = model.predict(test_X)
        test_X = test_X.reshape((test_X.shape[0], n_hours*n_features))
        inv_yhat = self.invert_scaling(yhat, test_X, n_features)
        return inv_yhat
    
    def make_actual(self, model, test_X, test_y, n_features = 1):
        test_X = test_X.reshape((test_X.shape[0], n_hours*n_features))
        test_y = test_y.reshape((len(test_y), 1))
        inv_y = self.invert_scaling(test_y, test_X, n_features)
        return inv_y

    def invert_scaling(self, test_y, test_X_reshape, n_features):
        inv_y = concatenate((test_y, test_X_reshape[:, -(n_features - 1):]), axis=1)
        inv_y = self.scaler.inverse_transform(inv_y)
        inv_y = inv_y[:,0]
        return inv_y

    def normalize_data(self, dataset, n_hours = 1, dropnan=True):
        values = dataset.values
        n_features = len(dataset.columns)
        values = values.astype('float32')
        scaled = self.scaler.fit_transform(values)
        reframed = self.series_to_supervised(scaled, n_hours, 1, dropnan)
        values = reframed.values
        return values, n_features

    def evaluate_model(self, inv_y, inv_yhat):
        max_error = 0
        for i in range(0,len(inv_y)):
            err = abs(inv_y[i] - inv_yhat[i])
            if err > max_error:
                max_error = err
        rmse = sqrt(mean_squared_error(inv_y, inv_yhat))
        return max_error, rmse

    def split_train_test(self, values, n_time_predicts):
        n_train_hours = len(values) - n_time_predicts
        train = values[:n_train_hours, :]
        test = values[n_train_hours:, :]
        return train, test

    def split_into_inputs_and_outputs(self, values, n_features = 10, n_hours = 1):
        n_time_predicts = len(values)
        n_obs = n_hours * n_features
        test_X, test_y = values[:, :n_obs], values[:, -n_features]
        test_X = test_X.reshape((n_time_predicts, n_hours, n_features))
        return test_X, test_y

    def fit_model(self, model, train_X, train_y, test_X, test_y, symbol, config):
        epochs, batch_size, verbose, min_delta, patience, monitor = config
        model.fit(train_X, train_y, epochs=epochs, batch_size=batch_size, verbose=verbose, shuffle=False, validation_data=(test_X, test_y),
            callbacks = [EarlyStopping(monitor=monitor, min_delta=min_delta, patience=patience)])
        return model
    
    def save_model(self, model, symbol):
        model.save_weights("weights/weight_%s.h5"%symbol)
        model_json = model.to_json()
        with open("models/model_%s.json"%symbol, "w") as json_file:
            json_file.write(model_json)

    def save_to_db(self, inv_y, inv_yhat, id_coin):
        max_openTime = self.db.get_max_open_time(id_coin)
        max_error, RMSE = self.evaluate_model(inv_y, inv_yhat)
        openTime_last = max_openTime - self.n_time_predicts * 60 * 60 * 1000
        time_create = int(time.time())
        price_predict = array2string(inv_yhat, separator=',')
        price_test = array2string(inv_y, separator=',')
        self.db.insert_history_train(id_coin, time_create, price_test, price_predict, RMSE, max_error, openTime_last)

    def train_model(self):
        dataset = self.db.get_data_train_by_id(coin[self.ID_COIN])
        values, n_features = self.normalize_data(dataset, self.n_hours)
        train, test = self.split_train_test(values, self.n_time_predicts)
        train_X, train_y = self.split_into_inputs_and_outputs(train, self.n_hours, n_features)
        test_X, test_y = self.split_into_inputs_and_outputs(test, self.n_hours, n_features)
        model = self.build_model(units=self.units, train_X = train_X)
        model = self.fit_model(model, train_X, train_y, test_X, test_y, coin[self.SYMBOL], self.config_train)
        self.save_model(model, coin[self.SYMBOL])
        inv_yhat = self.make_predict(model, test_X, self.n_hours, n_features)
        inv_y = self.make_actual(model, test_X, test_y, n_features)
        inv_yhat = inv_yhat[:-1]
        inv_y = inv_y[1:]
        self.save_to_db(inv_y, inv_yhat, coin[self.ID_COIN])
        self.save_img_predict_test(inv_y, inv_yhat, coin[self.SYMBOL])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Predict coin price.")
    parser.add_argument('-id',type=int,help="-id id coin")
    parser.add_argument('-symbol',type=str,help="-symbol symbol coin")
    args = parser.parse_args()
    coin = [args.symbol, args.id]
    units = 64
    n_hours = 1
    n_time_predicts = 2 * 24
    epochs = 50
    batch_size = 128
    verbose = 0
    min_delta = 1e-15
    patience = 30
    monitor = 'val_loss'

    config_train = (epochs, batch_size, verbose, min_delta, patience, monitor)
    trainModel = trainModel(coin , n_hours, n_time_predicts, config_train, units)
    trainModel.train_model()