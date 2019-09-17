import requests

class PinataGateway:

    # Verifies if API Keys are valid, throws if not
    def __init__(self, api_key,secret_api_key):
        self.headers = {'pinata_api_key':api_key, 'pinata_secret_api_key':secret_api_key}
        r = requests.get('https://api.pinata.cloud/data/testAuthentication', headers = self.headers)
        r.raise_for_status()
        
    def jsonUpload(self,payload):
        r = requests.post("https://api.pinata.cloud/pinning/pinJSONToIPFS",headers=self.headers, json = payload)
        r.raise_for_status()
        return r.json()

    def fileUpload(self,filename):
        f = open(filename,'rb')
        files = { 'file' : f}
        r = requests.post('https://api.pinata.cloud/pinning/pinFileToIPFS',headers=self.headers, files = files)
        f.close()
        r.raise_for_status()
        return r.json()
