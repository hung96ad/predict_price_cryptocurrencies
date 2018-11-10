from numpy import array2string
from numpy import delete
from numpy import s_
from numpy import concatenate
from keras.models import model_from_json
from sklearn.preprocessing import MinMaxScaler
from connectDB import ConnectDB
import argparse
import time

class Predict(object):
    SYMBOL = 0
    ID_COIN = 1

    def __init__(self):
        self.db = ConnectDB()
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.n_hours = 1

    def get_y(self, values):
        test_y = delete(values, s_[1:], 1)
        return test_y
    
    def load_model(self):
        json_file = open('models/model_%s.json'%coin[self.SYMBOL], 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        model = model_from_json(loaded_model_json)
        model.load_weights("weights/weight_%s.h5"%coin[self.SYMBOL])
        return model

    def save_to_db(self, inv_yhat, inv_y, id_coin):
        time_create = int(time.time())
        price_predict = array2string(inv_yhat, separator=',')
        price_actual = array2string(inv_y, separator=',')
        price_preidct_last = inv_yhat[-1]
        price_predict_previous = inv_yhat[-2]
        price_actual_last = inv_y[-1]
        price_actual_previous = inv_y[-2]
        self.db.insert_history_prediction(id_coin, time_create, price_actual, price_predict, 
            price_preidct_last, price_predict_previous, price_actual_last, price_actual_previous)

    def normalize_data(self, dataset, n_time_predicts=1, n_features=1, dropnan=True):
        values = dataset.values
        values = values.astype('float32')
        values = self.scaler.fit_transform(values)
        values = values.reshape((n_time_predicts, 1, n_features))
        return values

    def make_predict(self, model, test_X, n_features = 1):
        yhat = model.predict(test_X)
        test_X = test_X.reshape((test_X.shape[0], self.n_hours*n_features))
        inv_yhat = self.invert_scaling(yhat, test_X, n_features)
        return inv_yhat

    def invert_scaling(self, test_y, test_X_reshape, n_features):
        inv_y = concatenate((test_y, test_X_reshape[:, -(n_features - 1):]), axis=1)
        inv_y = self.scaler.inverse_transform(inv_y)
        inv_y = inv_y[:,0]
        return inv_y

    def make_predict_price_coin(self, coin):
        dataset = self.db.get_data_predict_by_id(coin[self.ID_COIN])
        inv_y = self.get_y(dataset.values)
        n_features = len(dataset.columns)
        n_time_predicts = len(dataset)
        test_X = self.normalize_data(dataset, n_time_predicts=n_time_predicts, n_features=n_features)
        model = self.load_model()
        inv_yhat = self.make_predict(model, test_X, n_features=n_features)
        self.save_to_db(inv_yhat, inv_y, coin[self.ID_COIN])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Forecast coin price with deep learning.")
    parser.add_argument('-id',type=int,help="-id id coin")
    parser.add_argument('-symbol',type=str,help="-symbol symbol coin")
    args = parser.parse_args()
    coin = [args.symbol, args.id]
    predict = Predict()
    predict.make_predict_price_coin(coin)