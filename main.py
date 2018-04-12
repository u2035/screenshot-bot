import sqlalchemy
import requests
import datetime
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
from db import zcreate, zget, zupdate
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

NTI_CLIENT_ID = 'd9c93c179463b5db1004'
updater = Updater(token='555211936:AAGxdfTtzjYHSK0G33oaMgT0o45VQ5vkaU0')


def reminder(bot, job_queue):
    chat_id = job_queue.context

    if zget(chat_id)['status'] != 2:
        job_queue.schedule_removal()
        zupdate(chat_id, status=3)
        return

    bot.send_message(chat_id=chat_id, text="Прошла еще минута...")



def timeup(bot, job_queue):
    chat_id = job_queue.context
    if zget(chat_id)['status'] != 2:
        job_queue.schedule_removal()
        return

    zupdate(chat_id, status=3)
    bot.send_message(chat_id=chat_id, text="К сожалению, время истекло. Фотографии, отпрвленные после этого сообщения не учитываются. Участвуйте в других активностях отбора, чтобы получить дополнительные баллы.")


def echo(bot, update):
    chat_id = update.message.from_user.id
    nk = ReplyKeyboardMarkup([[InlineKeyboardButton("Готов")]])

    try:
        zcreate(telegram_id=update.message.from_user.id, status=-2)
    except sqlalchemy.exc.IntegrityError: pass

    stt = zget(chat_id)['status']

    if stt == -2:
        update.message.reply_text('Добро пожаловать на оперативную задачу 10.21. Укажите свой идентификатор.')
        zupdate(chat_id, status=-1)
        return

    elif stt == -1:
        try:
            code = update.message.text.lower().strip()
        except AttributeError:
            update.message.reply_text('Пожалуйста, укажите ваш идентификатор.')
            return

        zupdate(chat_id, unti_code=code, status=0)
        update.message.reply_text('Принято. Теперь укажите свой ПИН.')
        return

    elif stt == 0:
        try:
            pin=update.message.text.lower().strip()
        except AttributeError:
            update.message.reply_text('Пожалуйста, укажите ваш ПИН.')
            return

        uid = zget(chat_id)['unti_code']

        rt = requests.get('https://sso.2035.university/auth_by_pin?unti_id={0}&pin={1}&client_id={2}'.format(uid, pin, NTI_CLIENT_ID))

        if rt.status_code == 200:
            zupdate(chat_id, status=1)
            rgdata  = rt.json()
            update.message.reply_text('Принято. Вы авторизованы как {0} {1}. Откройте чат с телефона с быстрым интернетом (3g/4g, WI-FI) и напишите "готов", когда сможете продолжить.'.format(rgdata['firstname'], rgdata['lastname']), reply_markup=nk)
        else:
            zupdate(chat_id, status=-1)
            update.message.reply_text('Вы не были идентифицированы. Укажите свой идентификатор еще раз.')

        return

    elif stt == 1:
        if update.message.text.lower().strip() == 'готов':
            zupdate(chat_id, status=2)
            update.message.reply_text('Отправьте скриншот своего рабочего стола на телефоне. У вас 3 минуты.', reply_markup=ReplyKeyboardRemove())
            updater.job_queue.run_repeating(reminder, interval=60, first=60, context=update.message.chat_id)
            updater.job_queue.run_once(timeup, 60*3, context=update.message.chat_id)
            return
        else:
            update.message.reply_text('Включите режим "готов"', reply_markup=nk)
            return



    elif stt == 2:
        if update.message.photo:
            ip = update.message.photo[-1]
            bot.getFile(ip.file_id).download("R_"+str(chat_id)+'_'+str(datetime.datetime.now().timestamp())+'.png')

            zupdate(chat_id, status=5)
            update.message.reply_text("Фотография сохранена. Спасибо за участие!")
        else:
            update.message.reply_text("Пожалуйста, отправьте фотографию.")
        return



    else:
        update.message.reply_text('Вы не можете решать эту задачу еще раз.')
        return


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text | Filters.photo | Filters.command, echo))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
