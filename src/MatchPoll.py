import datetime
import logging

import tzlocal

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger("footballteambot.MatchPoll")
logger.setLevel(logging.DEBUG)

available_options = ['Disponible', 'Duda (indica cuándo podrás confirmar)', 'Baja']

class MatchPoll:
    def __init__(self, poll_id, created_at):
        self.poll_id = poll_id
        self.created_at = created_at
        self.options = available_options
        self.votes = {}
        self.deadline = created_at + datetime.timedelta(days=4)

    def add_vote(self, user_id, option, timestamp):
        logger.debug(f"Adding vote: user_id={user_id}, option={option}, timestamp={timestamp}")
        if user_id not in self.votes:
            self.votes[str(user_id)] = Vote(user_id, option, timestamp)
            logger.debug(f"Vote added: {self.votes[(str(user_id))]}")

    def is_active(self):
        return datetime.datetime.now(tz=tzlocal.get_localzone()) < self.deadline

    def available_players(self):
        return [vote.user_id for vote in self.votes.values() if vote.is_available()]

    def unavailable_players(self):
        return [vote.user_id for vote in self.votes.values() if vote.is_unavailable()]

    def report(self, members = {}):
        logger.debug(f"Generating report for poll {self.poll_id}. Votes: {self.votes}, Members: {members}")
        report_lines = [f"<u><b>REPORTE ACTUAL DE LA CONVOCATORIA {self.created_at.strftime('%d-%m-%Y %H:%M')}</b></u>", "Votos:"]
        for user_id, vote in self.votes.items():
            user_name = members[str(user_id)]['username']
            logger.debug(f"Member: {members[str(user_id)]}")
            full_name = members[str(user_id)]['full_name']
            timestamp_str = vote.timestamp.strftime("%Y-%m-%d %H:%M")
            user_html_mention = f'<a href="https://t.me/{user_name}">@{user_name}</a>' if (user_name) else f'<a href="tg://user?id={user_id}">{full_name}</a>'
            report_lines.append(f"{user_html_mention} : {vote.option} (Marca temporal: {timestamp_str})")

        voted_user_ids = set(self.votes.keys())
        logger.debug(f"Voted user IDs: {voted_user_ids}")
        for user_id, user_info in members.items():
            logger.debug(f"Checking member: user_id={user_id}, user_info={user_info}")
            if str(user_id) not in voted_user_ids:
                user_name = members[str(user_id)]['username']
                logger.debug(f"Member: {members[str(user_id)]}")
                full_name = members[str(user_id)]['full_name']
                logger.debug(f"User {user_info['full_name']} (ID: {user_id}) has not voted yet.")
                user_html_mention = f'<a href="https://t.me/{user_name}">@{user_name}</a>' if (user_name) else f'<a href="tg://user?id={user_id}">{full_name}</a>'
                report_lines.append(f"{user_html_mention} aún no ha votado.")

        report_lines.append(f"<u>Cierre de la convocatoria: {self.deadline.strftime('%d-%m-%Y %H:%M')}</u>")
        return "\n\n".join(report_lines)
   
    def __repr__(self):
        return f"MatchPoll(poll_id={self.poll_id}, created_at={self.created_at}, votes={self.votes})"

class Vote:
    def __init__(self, user_id, option, timestamp):
        self.user_id = user_id
        self.option = option
        self.timestamp = timestamp

    def is_available(self):
        return self.option == 'Disponible'

    def is_unavailable(self):
        return not self.is_available()

    def __repr__(self):
        return f"Vote(user_id={self.user_id}, option={self.option}, timestamp={self.timestamp})"
    
    def __eq__(self, value : 'Vote'):
        self.user_id == value.user_id and self.option == value.option