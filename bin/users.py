import json

class Users():
    def __init__(self, data_path:str, logging):
        self.data_path = data_path
        self.logging = logging


    def writeToJson(self, raw_data:dict, user_id:str):
        """Writes the data to a json file
        """
        json_file = f'{self.data_path}/users/{user_id}.json'

        with open(json_file, 'w') as f:
            json.dump(raw_data, f)
            f.close()

    def readUsrJson(self, user_id :str):
        """ Returns a dict of whatever is in the json file. 
            If no file is found, it will return a string,
            if there is a decoding error, it will return a string.
        """
        json_file = f'{self.data_path}/users/{user_id}.json'
        # logging.info(f'Attempting to read json from {json_file}')
        try:
            with open(json_file) as f:
                data = json.load(f)
                f.close()
            # logging.warning(f'JSON for {user_id} loaded!')
            return data
        except json.decoder.JSONDecodeError as e:
            # logging.error('Couldnt retrieve json file for %s!' % user_id)
            return f"Decoding error {json_file}"
        except FileNotFoundError as e:
            # logging.error(f'File not found. {json_file}')
            return f"File not found {json_file}"

    def add_entry(self, word :str, message):
        """ Adds an incident to the users json file.
        
        """
        user_id = message.author.id
        server_id = str(message.guild.id)
        message_link = 'https://discordapp.com/channels/%s/%s/%s' % (server_id, message.channel.id, message.id)
        # json_file = '%s/data/users/%s.json' % (dir, user_id)
        json_file = f'{self.data_path}/users/{user_id}.json'

        new_evidence = {
            "timeSent": str(message.created_at),
            "message": message.content,
            "link": message_link
        }

        new_word = {
            word:{
                "evidence":[new_evidence]
            }
        }

        new_server = {
            server_id:new_word
        }

        data = self.readUsrJson(user_id)
        if not isinstance(data, dict):
            if "File not found" in data:
                first = {
                    "servers": new_server
                }
                self.writeToJson(first, user_id)
                return
            else:
                self.logging.warning(f'Something terrible has happened! {data}')

        # see if server exists, add new server if not

        try:
            data['servers'][server_id]
        except KeyError as e:
            data['servers'].update(new_server)
            self.writeToJson(data, json_file)
            return
        
        # see if word exists, add new word if not

        try:
            data['servers'][server_id][word]
        except KeyError as e:
            data['servers'][server_id].update(new_word)
            self.writeToJson(data, user_id)
            return
            
        # add evidence

        data['servers'][server_id][word]['evidence'].append(new_evidence)
        self.writeToJson(data, user_id)
        return