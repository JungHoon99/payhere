from sqlalchemy import *
from sqlalchemy.orm import sessionmaker

DB_URL = 'mysql+pymysql://root:kmk20216*@127.0.0.1:3306/payhere'


class engineconn:

    def __init__(self):
        self.engine = create_engine(DB_URL, pool_recycle = 500)

    def sessionmaker(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        return session

    def connection(self):
        conn = self.engine.connect()
        return conn
    
    
if __name__ == "__main__":
    engine = engineconn()
    session = engine.sessionmaker()