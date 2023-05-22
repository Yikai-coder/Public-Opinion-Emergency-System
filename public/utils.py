from django.db import connection, close_old_connections
def check_connection():
    """检查数据库连接是否可用
    WARNING:频繁调用会导致MySQL数据库丢失连接
    Returns:
        _type_: _description_
    """
    # try:
    #     connection.connection.ping()
    # except:
    #     connection.close()
    #     return False
    # else:
    #     return True
    close_old_connections()