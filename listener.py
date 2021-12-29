from telegram.ext import Updater, CallbackContext, CommandHandler
from telegram import Update
import os, app

telegram_token = os.getenv('TELEGRAM_KEY')
updater = Updater(telegram_token, use_context=True)
dispatcher = updater.dispatcher

def listenToTelegram():
    start_handler = CommandHandler('start', start, run_async=True)
    dispatcher.add_handler(start_handler)

    totalOrders_handler = CommandHandler('total_orders', returnTotalOrders, run_async=True)
    dispatcher.add_handler(totalOrders_handler)

    totalProfit_handler = CommandHandler('total_profits', returnTotalProfits, run_async=True)
    dispatcher.add_handler(totalProfit_handler)

    status_handler = CommandHandler('status', status, run_async=True)
    dispatcher.add_handler(status_handler)

    stopNew_handler = CommandHandler('stop_new', stopNew, run_async=True)
    dispatcher.add_handler(stopNew_handler)

    startNew_handler = CommandHandler('start_new', startNew, run_async=True)
    dispatcher.add_handler(startNew_handler)

    areYouOk_handler = CommandHandler('are_you_ok', iAmOk, run_async=True)
    dispatcher.add_handler(areYouOk_handler)

    currentProfit_handler = CommandHandler('current_profit', currentProfit, run_async=True)
    dispatcher.add_handler(currentProfit_handler)

    whenBought_handler = CommandHandler('when_bought', whenBought, run_async=True)
    dispatcher.add_handler(whenBought_handler)

    updater.start_polling()

def returnTotalOrders(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text=f'Total Orders:{app.orderCounter} \n{app.totalOrders}')

def returnTotalProfits(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text=f'Total Profits:\n{str(app.totalProfits)[:4]}%')

def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text=f'---------------------------------------------------------')
    print('---------------------------------------------------------')
    app.run(update, context)

def stopNew(update: Update, context: CallbackContext):
    app.startNew = False

def startNew(update: Update, context: CallbackContext):
    app.startNew = True

def iAmOk(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text='I Am Ok Alexander, Thanks For Asking. 💚💻')

def status(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text=app.run)

def currentProfit(update: Update, context: CallbackContext):
    if app.currentProfitFromOrder:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'Current Profit: {str(app.currentProfitFromOrder)[:5]}')
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'There is not order available')

def whenBought(update: Update, context: CallbackContext):
    if app.buyPrice:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'{app.CryptoToTrade}:{app.buyPrice}')
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'There is not order available')

print('Listening...')
listenToTelegram()