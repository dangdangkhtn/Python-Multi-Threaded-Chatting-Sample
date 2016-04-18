import json

DB_file = 'Credentials.json'


class Authenticate:
    Credentials = {}
    ''' Credentials would be like this:

    Credentials = {
        "usr_name_01": "password_01",
        .....
    }
    '''
    def __init__(self):
        with open(DB_file, 'r') as json_file:
            encoded_json = json_file.read()
            self.Credentials = json.loads(encoded_json)
        json_file.close()

    def register(self, usr_name, pwd):
        json_file = open(DB_file, 'w')
        self.Credentials.update({usr_name: pwd})
        json_str = json.dumps(self.Credentials)
        json_file.write(json_str)
        json_file.close()

    def authenticate(self, usr_name, pwd):
        if usr_name in self.Credentials:
            if self.Credentials[usr_name] == pwd:
                return True
        return False

    def account_registered(self, usr_name):
        if usr_name in self.Credentials:
            return True
        return False
