from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from typing import Final 
import random
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv('TOKEN')
BOT_USERNAME = os.getenv('BOT_USERNAME')

# In-memory user data to store balances
user_data = {}

# Helper function to get or initialize a user's balance
def get_balance(user_id: int) -> int:
    return user_data.get(user_id, 1000)  # Default balance of 1000 if new user

#Define basic bot commands
async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id   # Get user id
    user_name = update.message.from_user.first_name   # Get name of a user
    user_data[user_id] = get_balance(user_id)   # Initialize balance if needed
    logger.info(f"User {user_name} (ID: {user_id}) started the bot.")  # Log user start
    await update.message.reply_text(f"Hello {user_name}, welcome to the Gambling Bot! Use /balance to check your balance or /bet to place a bet.")

async def balance(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_balance = get_balance(user_id)
    logger.info(f"User {user_id} checked their balance: ${user_balance}.")  # Log balance check
    await update.message.reply_text(f"Your balance is ${user_balance}.")

async def bet(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    logger.info(f"User {user_id} attempted to place a bet.")

    # Check if bet amount is provided
    if context.args:
        try:
            # Parse the betting amount
            bet_amount = int(context.args[0])
            logger.info(f"User {user_id} bet amount: ${bet_amount}.")  # Log bet amount
        except ValueError:
            await update.message.reply_text("Please enter a valid number for your bet.")
            logger.error(f"User {user_id} provided an invalid bet amount: {context.args[0]}.")  # Log error
            return
    else:
        await update.message.reply_text("Please specify an amount to bet, like: /bet 50")
        logger.warning(f"User {user_id} did not specify a bet amount.")  # Log warning
        return

    user_balance = get_balance(user_id)

    # Check if the user has enough balance
    if bet_amount > user_balance:
        await update.message.reply_text("You don't have enough balance to place this bet.")
        logger.warning(f"User {user_id} attempted to bet ${bet_amount} with insufficient balance: ${user_balance}.")  # Log warning
        return
    elif bet_amount <= 0:
        await update.message.reply_text("Please enter a positive betting amount.")
        logger.warning(f"User {user_id} attempted to bet a non-positive amount: ${bet_amount}.")  # Log warning
        return

    # Deduct the bet amount from user's balance temporarily
    user_data[user_id] = user_balance - bet_amount

    # Simulate the game (coin flip)
    outcome = random.choice(['win', 'lose'])
    if outcome == 'win':
        # Double the bet amount if the user wins
        winnings = bet_amount * 2
        user_data[user_id] += winnings
        await update.message.reply_text(f"🎉 You won! You gained ${winnings}. Your new balance is ${user_data[user_id]}.")
        logger.info(f"User {user_id} won ${winnings}. New balance: ${user_data[user_id]}.")  # Log win
    else:
        # User loses the bet amount
        await update.message.reply_text(f"😞 You lost ${bet_amount}. Your new balance is ${user_data[user_id]}.")
        logger.info(f"User {user_id} lost ${bet_amount}. New balance: ${user_data[user_id]}.")  # Log loss


def main():
    # Initialize the bot application with the token
    application = Application.builder().token(TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CommandHandler("bet", bet))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
