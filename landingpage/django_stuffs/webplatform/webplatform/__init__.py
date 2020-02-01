'''try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass'''


import pymysql
pymysql.version_info = (0,9,8, "final", 0)#(1, 3, 13, "final", 0)
pymysql.install_as_MySQLdb()
