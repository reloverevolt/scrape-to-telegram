import telegram
from telegram.ext import Updater, CallbackQueryHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton 
import os


TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL = os.environ.get("CHANNEL_ID")
PORT = int(os.environ.get("PORT", 5000))

def handle_feedback(update, context):

	query = update.callback_query
	query.answer()

	cb_data = update.callback_query.data
	msg_id = str(update.effective_message.message_id)
	user_id = str(update.effective_user.id)
	

	if cb_data == "discuss":
		context.bot.forward_message(chat_id=os.environ.get("CHAT_ID"), from_chat_id=CHANNEL, message_id=msg_id)

	else:
		reaction = cb_data.split()[0]
		curr_reaction_count = int(cb_data.split()[1])
	
		try:
			fb_storage = context.chat_data[msg_id]
			try:
				fb_storage_reaction_ulist = fb_storage[reaction]
				fb_storage_reaction_ulist.remove(user_id)
				fb_storage[reaction] = fb_storage_reaction_ulist

				curr_reaction_count -= 1
		
			except KeyError:
				fb_storage[reaction] = [user_id]
	
				curr_reaction_count += 1

			except ValueError:	
				fb_storage_reaction_ulist.append(user_id)
				fb_storage[reaction] = fb_storage_reaction_ulist

				curr_reaction_count += 1


		except KeyError:
			context.chat_data[msg_id] = {}
			context.chat_data[msg_id][reaction] = [user_id]

			curr_reaction_count += 1


	# 3) Generating Updating new InlineKeyboardMarkup 
	
		curr_kbrd = update.effective_message.reply_markup.to_dict()

		like_btn_text, like_btn_cbd = curr_kbrd["inline_keyboard"][0][0].values()
		shit_btn_text, shit_btn_cbd = curr_kbrd["inline_keyboard"][0][1].values()
		want_btn_text, want_btn_url = curr_kbrd["inline_keyboard"][0][2].values()
		discuss_btn_text, discuss_btn_url = curr_kbrd["inline_keyboard"][1][0].values()
	

		if reaction == "like":
	
			like_btn_text = f"❤️{curr_reaction_count}"
			like_btn_cbd = f"like {curr_reaction_count}"

		elif reaction == "shit":

			shit_btn_text = f"💩{curr_reaction_count}"
			shit_btn_cbd = f"shit {curr_reaction_count}"


		reply_markup = InlineKeyboardMarkup([
			[
			InlineKeyboardButton(text=like_btn_text, callback_data=like_btn_cbd),
			InlineKeyboardButton(text=shit_btn_text, callback_data=shit_btn_cbd),
			InlineKeyboardButton(text=want_btn_text, url=want_btn_url)
			],
			[InlineKeyboardButton(text=discuss_btn_text, url=discuss_btn_url)]
			])

		context.bot.edit_message_reply_markup(
			chat_id=os.environ.get("CHANNEL_ID"), message_id=msg_id, reply_markup=reply_markup
			)	



def main():

	updater = Updater(token=TOKEN, use_context=True)
	dp = updater.dispatcher

	feedback_handler = CallbackQueryHandler(handle_feedback)
	dp.add_handler(feedback_handler)

	updater.start_webhook(listen="0.0.0.0",
                      port=int(PORT),
                      url_path=TOKEN)

	updater.bot.set_webhook(os.environ.get("APP_URL") + TOKEN)
	updater.idle()







if __name__ == "__main__":
	
	main()

	