from subprocess import Popen, PIPE, STDOUT
from connectDB import ConnectDB
import time

if __name__ == '__main__':
    start_time_main = time.time()
    DB = ConnectDB()
    list_coin = DB.get_list_coin_info("ETH")
    for coin in list_coin:
        print(coin)
        start_time = time.time()
        p = Popen('python3 train.py -id %s -symbol %s'%(coin[1], coin[0]), shell=True, 
             stdout=PIPE, stderr=STDOUT)
        retval = p.wait()
        print("Time train: %f" %(time.time() - start_time))
        time.sleep(1)
    print("Total time train: %f" %(time.time() - start_time_main))
