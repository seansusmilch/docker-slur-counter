from tinydb import where
from tinydb.table import Table
from discord import Message
import logging as log 

class Users():
    def __init__(self, user_tabl:Table):
        self.user_tbl = user_tabl

    def add_entry(self, word :str, message:Message):
        """ Adds an incident to the users json file.    
        
        """
        log.info(f'MSG: {message}')
        log.info(f'GUILD: {message.guild}')

        user_id = message.author.id
        server_id = str(message.guild.id)
        message_link = 'https://discordapp.com/channels/%s/%s/%s' % (server_id, message.channel.id, message.id)

        # user_tbl = self.evidence_db.table(user_id)

        new_evidence = {
            "timeSent": str(message.created_at),
            "message": message.content,
            "link": message_link,
            "server": message.guild.id
        }

        if not self.user_tbl.contains(where('uid')==user_id):
            new_word = {
                'uid':user_id,
                word: [new_evidence]
            }
            self.user_tbl.insert(new_word)
            return
        old_doc = self.user_tbl.get(where('uid')==user_id)
        prev_evidence = old_doc[word] if word in old_doc.keys() else []
        # new_list = prev_evidence.append(new_evidence) if isinstance(prev_evidence,list) else [new_evidence]
        new_word = {
            word : prev_evidence + [new_evidence] if isinstance(prev_evidence,list) else [new_evidence]
        }
        self.user_tbl.update(new_word, where('uid')==user_id)