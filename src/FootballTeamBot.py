
import random
import logging

# from distutils.cmd import Command
import datetime
import re

from telegram import Update, User, Chat
from telegram.error import BadRequest
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, PollAnswerHandler, CallbackContext, MessageHandler, MessageReactionHandler, filters

from MatchPoll import MatchPoll, available_options
import json
import os

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger("footballteambot")
logger.setLevel(logging.DEBUG)
telegram_logger = logging.getLogger("telegram")
telegram_logger.setLevel(logging.DEBUG)

"""Football Telegram Bot

It models a telegram bot and perform some reactions to Telegram commands

"""
class FootballTeamBot:
    def __init__(self, token = "TOKEN") -> None:
        super().__init__()
        
        self.app = ApplicationBuilder().token(token).build()

        logger.info("Initializing bot")
        logger.info("Setting up handlers")
        
        logger.info("Setting up match poll handler")
        self.app.add_handler(MessageHandler(filters.StatusUpdate.FORUM_TOPIC_CREATED, self.handle_topic_created), group=0)
        self.app.add_handler(MessageHandler(filters.TEXT & filters.IS_TOPIC_MESSAGE, self.handle_first_message), group=1)
        self.app.add_handler(MessageHandler(filters.ALL, self.register_member), group=2)
        self.app.add_handler(MessageReactionHandler(self.register_member), group=3)
        self.app.add_handler(PollAnswerHandler(self.handle_vote))

        self.active_match_polls = self.load_active_match_polls("active_match_polls.json")
        self.pending_topics = {}
        self.chat_members = self.load_chat_members("chat_members.json")
        logger.debug(f"Loaded chat members: {self.chat_members}")

        # Daily report job
        logger.info("Scheduling daily report job")
        self.app.job_queue.run_repeating(self.daily_report, interval=60*60*24, first=60*60*12)

        logger.info("Starting bot")
        self.app.run_polling()

    def __del__(self):
        logger.info("Stopping bot")
        self.app.stop()
        logger.info("Shutting down bot")
        self.app.shutdown()

    def load_chat_members(self, filename):
        chat_members = {}
        if os.path.exists(filename):
            with open(filename, "r") as f:
                chat_members = json.load(f)
        return chat_members

    def save_chat_members(self, chat_members_file):
        with open(chat_members_file, "w") as f:
            json.dump(self.chat_members, f)
    
    def load_active_match_polls(self, filename):
        logger.debug(f"Loading active match polls from {filename}")
        active_match_polls = {}
        if os.path.exists(filename):
            with open(filename, "r") as f:
                data = json.load(f)
                for chat_id, topics in data.items():
                    active_match_polls[chat_id] = {}
                    for topic_id, polls in topics.items():
                        active_match_polls[chat_id][topic_id] = {}
                        for poll_id, poll_data in polls.items():
                            poll = MatchPoll(poll_data['poll_id'], datetime.datetime.fromisoformat(poll_data['created_at']))
                            for user_id, vote_data in poll_data['votes'].items():
                                poll.add_vote(vote_data['user_id'], vote_data['option'], datetime.datetime.fromisoformat(vote_data['timestamp']))
                            active_match_polls[chat_id][topic_id][poll_id] = poll

        logger.debug(f"Loaded active match polls: {active_match_polls}")
        return active_match_polls
    
    def save_active_match_polls(self, filename):
        data = {}
        for chat_id, topics in self.active_match_polls.items():
            data[chat_id] = {}
            for topic_id, polls in topics.items():
                data[chat_id][topic_id] = {}
                for poll_id, poll in polls.items():
                    data[chat_id][topic_id][poll_id] = {
                        'poll_id': poll.poll_id,
                        'created_at': poll.created_at.isoformat(),
                        'votes': {str(user_id): {'user_id': vote.user_id, 'option': vote.option, 'timestamp': vote.timestamp.isoformat()} for user_id, vote in poll.votes.items()}
                    }
        logger.debug(f"Saving active match polls: {data}")
        with open(filename, "w") as f:
            json.dump(data, f)
    

    async def stop_match_poll(self, context: ContextTypes.DEFAULT_TYPE, chat_id, topic_id, poll_id):
        logger.debug(f"Stopping poll {poll_id} in chat {chat_id}, topic {topic_id}")
        await context.bot.stop_poll(chat_id=chat_id, message_thread_id=topic_id, poll_id=poll_id)
        del self.active_match_polls[chat_id][topic_id][poll_id]
        logger.debug(f"Poll {poll_id} stopped and removed from active polls")
        await context.bot.send_message(chat_id=chat_id, message_thread_id=topic_id, text="Convocatòria tancada")

    async def register_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.debug(f"Received update {update}")
        msg = update.message
        user = msg.from_user
        chat = msg.chat
        await self.register_member_logic(user, chat)

    async def register_member_logic(self, user: User, chat: Chat):
        logger.debug(f"Registering member {user} in chat {chat}")
        chat_id_str = str(chat.id)
        if chat_id_str not in self.chat_members:
            self.chat_members[chat_id_str] = {}
        user_exists = str(user.id) in self.chat_members[chat_id_str]
        logger.debug(f"User exists: {user_exists} ({str(user.id) in self.chat_members[chat_id_str]})")
        logger.debug(f"Current members in chat {chat_id_str}: {self.chat_members[chat_id_str]}")
        logger.debug(f"Keys: {self.chat_members[chat_id_str].keys()}")
        if not user.is_bot and not user_exists:
            self.chat_members[chat_id_str][str(user.id)] = {"username": user.username, "full_name": user.full_name}
            logger.info(f"Registered member {user} in chat {chat_id}")
            self.save_chat_members("chat_members.json")


    def get_chat_id_from_poll_id(self, poll_id):
        for chat_id, topics in self.active_match_polls.items():
            for topic_id, polls in topics.items():
                if poll_id in polls:
                    return chat_id, topic_id
        return None, None

    async def check_topic_exists(self, context, chat_id, thread_id):
        try:
            # You can use send_message or get_forum_topic (if supported)
            await context.bot.get_forum_topic(chat_id, thread_id)
            return True
        except BadRequest as e:
            logger.debug(f"Error checking topic existence: {e}")
            if "message thread not found" in str(e):
                logger.info(f"Topic {thread_id} was deleted.")
                # Clean up local data here
                if thread_id in self.pending_topics:
                    await self.handle_topic_deleted(context, chat_id, thread_id)
                    return False
            else:
                raise
    
    async def daily_report(self, context: ContextTypes.DEFAULT_TYPE):
        for chat_id, topics in self.active_match_polls.items():
            logger.debug(f"Processing daily report for chat {chat_id}. Active topics: {topics.keys()}")
            for topic_id, polls in topics.items():
                logger.debug(f"Processing topic {topic_id} with polls: {polls.keys()}")
                for poll_id in polls:
                    poll: MatchPoll = polls[poll_id]
                    logger.debug(f"Processing poll {poll}")
                    if not poll.is_active():
                        logger.info(f"Poll {poll.poll_id} in chat {chat_id}, topic {topic_id} is not active anymore, stopping it")
                        await self.stop_match_poll(context, chat_id, topic_id, poll.poll_id)
                    else:
                        logger.info(f"Generating daily report for poll {poll.poll_id} in chat {chat_id}, topic {topic_id}")
                        members = self.chat_members[str(chat_id)]
                        logger.debug(f"Members: {members}")
                        report = poll.report(members)
                        await context.bot.send_message(chat_id=chat_id, message_thread_id=topic_id, text=report, parse_mode="HTML", disable_web_page_preview=True)

    async def make_match_poll(self, context: ContextTypes.DEFAULT_TYPE, chat_id, topic_id, question, options):
        logger.debug(f"Creating poll in chat {chat_id}, topic {topic_id} with question '{question}' and options {options}")
        poll_msg = await context.bot.send_poll(
            chat_id=chat_id,
            message_thread_id=topic_id,
            question=question,
            options=options,
            is_anonymous=False
        )
        logger.debug(f"Poll created: {poll_msg}")
        if chat_id not in self.active_match_polls:
            self.active_match_polls[chat_id] = {}
        
        if topic_id not in self.active_match_polls[chat_id]:
            self.active_match_polls[chat_id][topic_id] = {} 
        
        self.active_match_polls[chat_id][topic_id][poll_msg.poll.id] = MatchPoll(poll_msg.poll.id, datetime.datetime.now()) 

        logger.debug(f"Active polls updated: {self.active_match_polls}")

        self.save_active_match_polls("active_match_polls.json")

        await context.bot.pin_chat_message(chat_id=chat_id, message_id=poll_msg.message_id)

    async def handle_topic_created(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = update.message
        logger.debug(f'New topic message: {msg}')

        topic_title = msg.forum_topic_created and msg.forum_topic_created.name
        thread_id = msg.message_thread_id

        logger.debug(f"New topic created: {topic_title} in thread {thread_id}")

        if not topic_title:
            return

        if re.match(r"^[JA]\d+\s*-", topic_title):
            self.pending_topics[thread_id] = topic_title
            logger.debug(f"Detected new matching topic: {topic_title}")
            # Wait for first message — do NOT create poll yet

    async def handle_first_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = update.message
        thread_id = msg.message_thread_id
        
        logger.debug(f"First message {msg} in thread {thread_id}")
        # Check if this thread is in pending topics
        if thread_id in self.pending_topics:
            topic_title = self.pending_topics.pop(thread_id)
            logger.debug(f"First message in topic '{topic_title}', creating poll...")
            await self.make_match_poll(context, msg.chat.id, msg.message_thread_id, "Indica tu disponibilidad", available_options)

    async def handle_topic_deleted(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = update.message
        thread_id = msg.message_thread_id
        chat_id = msg.chat.id

        logger.debug(f"Topic deleted in thread {thread_id}")

        if chat_id in self.active_match_polls and thread_id in self.active_match_polls[chat_id]:
            poll = self.active_match_polls[chat_id][thread_id]
            await self.stop_match_poll(context, chat_id, thread_id, poll.poll_id)
    
    async def handle_vote(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.debug(f"Handling update {update}")
        logger.debug(f"Received poll answer: {update.poll_answer}")

        if not update.poll_answer:
            return

        await self.register_member_logic(update.poll_answer.user, update.effective_chat)

        poll_answer = update.poll_answer
        user_id = poll_answer.user.id
        poll_id = poll_answer.poll_id
        chat_id, topic_id = self.get_chat_id_from_poll_id(poll_id)
        option_ids = poll_answer.option_ids
        logger.debug(f"Vote from user {user_id} in chat {chat_id}, topic {topic_id}, options {option_ids}")

        if not chat_id or not topic_id:
            return
        
        if len(option_ids) != 1:
            logger.debug("Multiple options selected, ignoring")
            return

        poll: MatchPoll = self.active_match_polls[chat_id][topic_id][poll_id]
        logger.debug(f"Found poll: {poll}")
        if not poll.is_active():
            logger.info("Poll is not active anymore")
            await self.stop_match_poll(context, chat_id, topic_id, poll.poll_id)
            return

        option_id = option_ids[0]
        if option_id < 0 or option_id >= len(poll.options):
            return

        option = list(poll.options)[option_id]
        timestamp = datetime.datetime.now()
        poll.add_vote(user_id, option, timestamp)


