from subprocess import Popen, PIPE, STDOUT
from connectDB import ConnectDB
from crawler_data_binance import crawlerDataBinance
import time

if __name__ == '__main__':
    start_time = time.time()
    # get data from Binance
    crawler = crawlerDataBinance()
    crawler.insert_coin_info_to_db()
    crawler.insert_symbols_candlestick_data()
    print("Total time get data: %f"%(time.time() - start_time))
    start_time = time.time()
    # predict data
    DB = ConnectDB()
    list_coin = DB.get_list_coin_info("ETH")
    for coin in list_coin:
        print(coin)
        p = Popen('python3 predict.py -id %s -symbol %s'%(coin[1], coin[0]), shell=True, 
             stdout=PIPE, stderr=STDOUT)
        retval = p.wait()
    print("Total time predict: %f" %(time.time() - start_time))