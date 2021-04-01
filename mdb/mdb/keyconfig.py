import os

class Database:
  NAME = os.getenv('POSTGRES_DB')
  USER = os.getenv('POSTGRES_USER')
  PASSWORD = os.getenv('POSTGRES_PASSWORD')
  HOST = os.getenv('DATABASE_HOST')
  PORT = os.getenv('DATABASE_PORT')
  SECRET_KEY = os.getenv('SECRET_KEY')
  def __init__(self, *args, **kwargs):
    print('keyconfig.py init', os.getenv('DATABASE'))
    self.NAME = os.getenv('POSTGRES_DB')
    self.USER = os.getenv('POSTGRES_USER')
    self.PASSWORD = os.getenv('POSTGRES_PASSWORD')
    self.HOST = os.getenv('DATABASE_HOST')
    self.PORT = os.getenv('DATABASE_PORT')
    self.SECRET_KEY = os.getenv('SECRET_KEY')

