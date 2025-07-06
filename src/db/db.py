from config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

print(settings.db_url)

engine = create_engine(settings.db_url, echo=True)

Session = sessionmaker(bind=engine)

session = Session()

if __name__ == '__main__':
    with engine.connect() as connection:
        print('connected to database lol')
