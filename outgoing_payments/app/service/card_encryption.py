from Crypto.Hash import SHA256, SHA1
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from base64 import b64encode
from Crypto.Signature import pss

path = "cardbankkey.pub"


def encrypt_card(card_number: str):
    with open(path, "r") as file:
        pubkey = file.read()

    keyPub = RSA.import_key(pubkey)

    cipher = PKCS1_OAEP.new(keyPub, SHA256, mgfunc=lambda x,
                            y: pss.MGF1(x, y, SHA1))
    cipher_text = cipher.encrypt(card_number.encode())
    encodedCard = b64encode(cipher_text)

    print(encodedCard)
    return encodedCard
