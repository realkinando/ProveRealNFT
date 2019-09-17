import unittest
from PinataGateway import PinataGateway
import random, string, requests, time

class TestPinataGateway(unittest.TestCase):

    def test_init(self):
        a = PinataGateway("b8e2622c756783c562e8","8f4d41219c8a17684825f0d94018225e755eef3eccde5f9202af468f2b8d4e0c")
        self.assertIsNotNone(a)

    def test_init_bad_keys(self):
        with self.assertRaises(Exception):
            PinataGateway("b8e261340134r8","8f4d41219c8a17684825fasfdaagadfa4e0c")

    def test_json(self):
        a = PinataGateway("b8e2622c756783c562e8","8f4d41219c8a17684825f0d94018225e755eef3eccde5f9202af468f2b8d4e0c")
        randomDictList = []
        ipfsHashList = []
        for i in range(2):
            randomDictList.append({
                "name":''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]),
                "description":''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]),
                "image_url":''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
                })
            ipfsHashList.append(a.jsonUpload(randomDictList[i])["IpfsHash"])
        for i in range(2):
            start = time.time()
            r = requests.get("https://gateway.pinata.cloud/ipfs/"+ipfsHashList[i])
            end  = time.time()
            print("Fetching JSON ",ipfsHashList[i]," from Pinata took ",end-start," s" )
            pinataData = r.json()
            self.assertEqual(randomDictList[i],pinataData)

    def test_bad_str_json(self):
        a = PinataGateway("b8e2622c756783c562e8","8f4d41219c8a17684825f0d94018225e755eef3eccde5f9202af468f2b8d4e0c")
        randomDictList = []
        with self.assertRaises(Exception):
            a.jsonUpload("nonsenseString")


    def test_fileUpload(self):
        a = PinataGateway("b8e2622c756783c562e8","8f4d41219c8a17684825f0d94018225e755eef3eccde5f9202af468f2b8d4e0c")
        randomStrList = []
        ipfsHashList = []
        for i in range(2):
            randomStrList.append(''.join([random.choice(string.ascii_letters + string.digits) for n in range(30000)]))
            f = open("test.txt","w")
            f.write(randomStrList[i])
            f.close()
            ipfsHashList.append(a.fileUpload("test.txt")["IpfsHash"])
        for i in range(2):
            start = time.time()
            r = requests.get("https://gateway.pinata.cloud/ipfs/"+ipfsHashList[i])
            end = time.time()
            print("Fetching string ",ipfsHashList[i]," from Pinata took ",end-start," s" )
            pinataData = r.text
            self.assertEqual(randomStrList[i],pinataData)

    def test_json_ipfsio(self):
        a = PinataGateway("b8e2622c756783c562e8","8f4d41219c8a17684825f0d94018225e755eef3eccde5f9202af468f2b8d4e0c")
        randomDictList = []
        ipfsHashList = []
        for i in range(2):
            randomDictList.append({
                "name":''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]),
                "description":''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]),
                "image_url":''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
                })
            ipfsHashList.append(a.jsonUpload(randomDictList[i])["IpfsHash"])
        for i in range(2):
            start = time.time()
            r = requests.get("https://ipfs.io/ipfs/"+ipfsHashList[i],timeout=30)
            end  = time.time()
            print("Fetching JSON ",ipfsHashList[i]," from ipfs.io took ",end-start," s" )
            ipfsData = r.json()
            self.assertEqual(randomDictList[i],ipfsData)


    def test_fileUpload_ipfsio(self):
        a = PinataGateway("b8e2622c756783c562e8","8f4d41219c8a17684825f0d94018225e755eef3eccde5f9202af468f2b8d4e0c")
        randomStrList = []
        ipfsHashList = []
        for i in range(2):
            randomStrList.append(''.join([random.choice(string.ascii_letters + string.digits) for n in range(30000)]))
            f = open("test.txt","w")
            f.write(randomStrList[i])
            f.close()
            ipfsHashList.append(a.fileUpload("test.txt")["IpfsHash"])
        for i in range(2):
            start = time.time()
            r = requests.get("https://ipfs.io/ipfs/"+ipfsHashList[i],timeout=90)
            end = time.time()
            print("Fetching string ",ipfsHashList[i]," from ipfs.io took ",end-start," s" )
            ipfsData = r.text
            self.assertEqual(randomStrList[i],ipfsaData)


if __name__ == '__main__':
    unittest.main()
