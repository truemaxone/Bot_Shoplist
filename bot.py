import handlers
from dispatcher import dp
from postgresdb import DB
from aiogram import executor


db = DB()


# Run
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
