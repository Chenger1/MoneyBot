from environs import Env

# Теперь используем вместо библиотеки python-dotenv библиотеку environs
env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")  # Забираем значение типа str
IP = env.str("ip")  # Тоже str, но для айпи адреса хоста
REDIS_HOST = 'localhost'
DB_PASSWORD = env.str('db_password')
DB_USER = env.str('db_user')
DB_NAME = env.str('db_name')
