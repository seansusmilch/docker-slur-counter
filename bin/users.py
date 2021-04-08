import json
from tinydb import TinyDB, where
from discord import Message
class Users():
    def __init__(self, logging, user_tabl):
        # self.data_path = data_path
        self.log = logging
        self.user_tbl = user_tabl

    # def writeToJson(self, raw_data:dict, user_id:str):
        # """Writes the data to a json file
        # """
        # self.log.info(f'Writing to json file for {user_id}')
        # json_file = f'{self.data_path}/users/{user_id}.json'

        # with open(json_file, 'w') as f:
        #     json.dump(raw_data, f)
        #     f.close()

    # def readUsrJson(self, user_id :str):
        # """ Returns a dict of whatever is in the json file. 
        #     If no file is found, it will return a string,
        #     if there is a decoding error, it will return a string.
        # """
        # self.log.info(f'Reading user json for {user_id}')
        # json_file = f'{self.data_path}/users/{user_id}.json'
        # self.log.info(f'Attempting to read json from {json_file}')
        # try:
        #     with open(json_file) as f:
        #         data = json.load(f)
        #         f.close()
        #     # self.logging.info(f'JSON: {data}')
        #     return data
        # except json.decoder.JSONDecodeError as e:
        #     self.log.error(f'Couldnt retrieve json file for {user_id}!')
        #     self.log.error(e.message)
        #     return f"Decoding error {json_file}"
        # except FileNotFoundError as e:
        #     self.log.error(f'File not found. {json_file}')
        #     return f"File not found {json_file}"

    # def add_entry(self, word :str, message):
        # """ Adds an incident to the users json file.
        
        # """
        # self.log.info(f'MSG: {message}')
        # self.log.info(f'GUILD: {message.guild}')

        # user_id = message.author.id
        # server_id = str(message.guild.id)
        # message_link = 'https://discordapp.com/channels/%s/%s/%s' % (server_id, message.channel.id, message.id)
        # # json_file = '%s/data/users/%s.json' % (dir, user_id)
        # json_file = f'{self.data_path}/users/{user_id}.json'

        # new_evidence = {
        #     "timeSent": str(message.created_at),
        #     "message": message.content,
        #     "link": message_link,
        #     "author": message.author.id
        # }

        # new_word = {
        #     word:{
        #         "evidence":[new_evidence]
        #     }
        # }

        # new_server = {
        #     server_id:new_word
        # }

        # data = self.readUsrJson(user_id)
        # if not isinstance(data, dict):
        #     if "File not found" in data:
        #         first = {
        #             "servers": new_server
        #         }
        #         self.writeToJson(first, user_id)
        #         return
        #     else:
        #         self.log.warning(f'Something terrible has happened! {data}')

        # # see if server exists, add new server if not

        # try:
        #     data['servers'][server_id]
        # except KeyError as e:
        #     data['servers'].update(new_server)
        #     self.writeToJson(data, json_file)
        #     return
        
        # # see if word exists, add new word if not

        # try:
        #     data['servers'][server_id][word]
        # except KeyError as e:
        #     data['servers'][server_id].update(new_word)
        #     self.writeToJson(data, user_id)
        #     return
            
        # # add evidence

        # data['servers'][server_id][word]['evidence'].append(new_evidence)
        # self.writeToJson(data, user_id)
        # return

    def add_entry(self, word :str, message:Message):
        """ Adds an incident to the users json file.    
        
        """
        self.log.info(f'MSG: {message}')
        self.log.info(f'GUILD: {message.guild}')

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