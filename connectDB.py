try:
    import mysql.connector as mysql
except :
    import MySQLdb  as mysql
from pandas import read_sql
from config_db import config_db

class ConnectDB(object):                 
    def get_data_train_by_id(self, id_coin):
        cnx = config_db()
        query_string = "SELECT c.openTime,\
                c.`close`,\
                c.high,\
                c.low,\
                c.`open`,\
                c.volume,\
                c.quoteAssetVolume,\
                c.numberOfTrader,\
                c.takerBuyBaseAssetVolume,\
                c.takerBuyQuoteAssetVolume,\
                c.`ignore`\
            FROM candlestick_data AS c\
            WHERE c.idCoin = %s"%(id_coin)
        history = read_sql(query_string, con=cnx, index_col="openTime")
        cnx.close()
        del cnx
        return history

    def get_data_predict_by_id(self, id_coin):
        cnx = config_db()
        query_string = "SELECT c.openTime,\
                c.`close`,\
                c.high,\
                c.low,\
                c.`open`,\
                c.volume,\
                c.quoteAssetVolume,\
                c.numberOfTrader,\
                c.takerBuyBaseAssetVolume,\
                c.takerBuyQuoteAssetVolume,\
                c.`IGNORE` \
            FROM candlestick_data AS c \
            JOIN (SELECT MAX(h.openTime_last) openTime_last, \
                        h.id_coin \
                    FROM historical_train AS h \
                    GROUP BY id_coin \
                    ) AS h \
                ON c.idCoin = %s \
                AND h.id_coin = c.idCoin \
                AND c.openTime > h.openTime_last"%(id_coin)
        history = read_sql(query_string, con=cnx, index_col="openTime")
        cnx.close()
        del cnx
        return history
    
    def get_data_train_univariate_by_id(self, id_coin):
        cnx = config_db()
        query_string = "SELECT c.openTime,\
                c.`close`\
            FROM candlestick_data AS c\
            WHERE c.idCoin = %s"%(id_coin)
        history = read_sql(query_string, con=cnx, index_col="openTime")
        cnx.close()
        del cnx
        return history

    def get_data_predict_univariate_by_id(self, id_coin):
        cnx = config_db()
        query_string = "SELECT c.openTime,\
                c.`close`\
            FROM candlestick_data AS c \
            JOIN (SELECT MAX(h.openTime_last) openTime_last, \
                        h.id_coin \
                    FROM historical_train AS h \
                    GROUP BY id_coin \
                    ) AS h \
                ON c.idCoin = %s \
                AND h.id_coin = c.idCoin \
                AND c.openTime > h.openTime_last"%(id_coin)
        history = read_sql(query_string, con=cnx, index_col="openTime")
        cnx.close()
        del cnx
        return history
        
    def get_max_open_time(self, id_coin):
        cnx = config_db()
        cursor = cnx.cursor()
        query_string = "SELECT MAX(openTime) \
                FROM candlestick_data \
                WHERE idCoin = %s "%id_coin
        cursor.execute(query_string)
        max_openTime = cursor.fetchall()
        cursor.close()
        cnx.close()
        del cursor
        del cnx
        return max_openTime[0][0]

    def get_list_coin_info(self, quoteAsset = "ETH"):
        cnx = config_db()
        cursor = cnx.cursor()
        query_string = "SELECT c.symbol, \
                c.id \
            FROM coin_info c \
            WHERE c.`status` = 'TRADING' \
                AND c.quoteAsset = '%s'"%quoteAsset
        cursor.execute(query_string)
        coins_info = cursor.fetchall()
        cursor.close()
        cnx.close()
        del cursor
        del cnx
        return coins_info

    def update_coin_info_by_id(self, openTime_last, max_error, RMSE, id_coin):
        cnx = config_db()
        cursor = cnx.cursor()
        query_string = "UPDATE coin_info\
            SET	openTime_last = %s, \
                max_error = %s, \
                RMSE = %s\
            WHERE id = %s"%(openTime_last, max_error, RMSE, id_coin)
        try:
            cursor.execute(query_string)
            cnx.commit()
        except mysql.Error as err:
            cnx.rollback()
            print("Something went wrong: {}".format(err))
        cursor.close()
        cnx.close()
        del cursor
        del cnx
        return None

    def insert_history_prediction(self, id_coin, time_create, price_actual, price_predict,
            price_preidct_last, price_predict_previous, price_actual_last, price_actual_previous):
        cnx = config_db()
        cursor = cnx.cursor()
        query_string = "INSERT INTO historical_price_predictions(id_coin, time_create, price_actual, price_predict, \
                price_preidct_last, price_predict_previous, price_actual_last, price_actual_previous)\
            VALUES (%s,%s,'%s','%s',%s,%s,%s,%s)"%(id_coin, time_create, price_actual, price_predict,
                price_preidct_last, price_predict_previous, price_actual_last, price_actual_previous)
        try:
            cursor.execute(query_string)
            cnx.commit()
        except mysql.Error as err:
            cnx.rollback()
            print("Something went wrong: {}".format(err))
        cursor.close()
        cnx.close()
        del cursor
        del cnx
        return None

    def insert_history_train(self, id_coin, time_create, price_test, price_predict, RMSE, max_error, openTime_last):
        cnx = config_db()
        cursor = cnx.cursor()
        query_string = "INSERT INTO historical_train(id_coin, time_create, price_test, price_predict, RMSE, max_error, openTime_last)\
            VALUES(%s,%s,'%s','%s',%s,%s,%s)"%(id_coin, time_create, price_test, price_predict, RMSE, max_error, openTime_last)
        try:
            cursor.execute(query_string)
            cnx.commit()
        except mysql.Error as err:
            cnx.rollback()
            print("Something went wrong: {}".format(err))
        cursor.close()
        cnx.close()
        del cursor
        del cnx
        return None