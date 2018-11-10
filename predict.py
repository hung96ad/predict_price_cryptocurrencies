from numpy import array2string
from numpy import delete
from numpy import s_
from train import trainModel
import time
from keras.models import model_from_json
import argparse

class Predict(object):
    SYMBOL = 0
    ID_COIN = 1

    def __init__(self):
        self.trainModel = trainModel()

    def get_y(self, values):
        test_y = delete(values, s_[1:], 1)
        test_y = delete(test_y, 0)
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
        self.trainModel.db.insert_history_prediction(id_coin, time_create, price_actual, price_predict, 
            price_preidct_last, price_predict_previous, price_actual_last, price_actual_previous)

    def make_predict_multiple_coin(self, coin):
        dataset = self.trainModel.db.get_data_predict_by_id(coin[self.ID_COIN])
        inv_y = self.get_y(dataset.values)
        values, n_features = self.trainModel.normalize_data(dataset, dropnan=False)
        test_X, test_y = self.trainModel.split_into_inputs_and_outputs(values,n_features=n_features)
        model = self.load_model()
        inv_yhat = self.trainModel.make_predict(model, test_X, n_features=n_features)
        self.save_to_db(inv_yhat, inv_y, coin[self.ID_COIN])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Forecast coin price with deep learning.")
    parser.add_argument('-id',type=int,help="-id id coin")
    parser.add_argument('-symbol',type=str,help="-symbol symbol coin")
    args = parser.parse_args()
    coin = [args.symbol, args.id]
    predict = Predict()
    predict.make_predict_multiple_coin(coin)