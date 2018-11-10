try:
    import mysql.connector as mysql
except :
    import MySQLdb  as mysql

def config_db():
    return mysql.connect(user='root', password='',
                            host='localhost',
                            database='coin')                        
