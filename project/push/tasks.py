"""
    The MIT License (MIT)
    Copyright (c) 2016 Fastboot Mobile LLC.

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from nacl import signing, encoding
from nacl.public import PrivateKey, PublicKey, Box
import nacl.utils
import json
import base64
import requests


def encrypt_data(private_hex, public_hex, message):
    sk = PrivateKey(private_hex, nacl.encoding.HexEncoder)
    pk = PublicKey(public_hex, nacl.encoding.HexEncoder)

    box = Box(sk, pk)
    nonce = nacl.utils.random(Box.NONCE_SIZE)

    encoded = box.encrypt(message.encode(), nonce, encoder=nacl.encoding.HexEncoder)
    return encoded


def generate_token(sig_key_hex, enc_key_hex, app_key, message, to):
    signing_key = signing.SigningKey(sig_key_hex, encoder=nacl.encoding.HexEncoder)

    to = app_key + "." + to  # combine the APP public key and the install ID

    # Setup header
    header_dict = {}
    header_dict['API_KEY'] = signing_key.verify_key.encode(encoder=nacl.encoding.HexEncoder).decode()  # Add api public key
    header_dict['alg'] = "FM-1"
    header_dict['typ'] = "JWT"
    header_dict['srv_v'] = "v0.0"
    header_dict['to'] = to  # Add the install public ID

    device_to_parts = to.split(".")

    header_txt = json.dumps(header_dict)  # create the header json

    encoded = encrypt_data(enc_key_hex, device_to_parts[1], message)  # encrypt the data with the install public key and the app private key

    txt = encoded.ciphertext  # get only the cipher text
    nonce = encoded.nonce  # get the nonce

    # create the token body
    body_dict = {}
    body_dict['data'] = txt.decode()
    body_dict['nonce'] = nonce.decode()
    body_txt = json.dumps(body_dict)

    # b64 encode the body and header of the token
    header_b64 = base64.b64encode(header_txt.encode()).decode()
    body_b64 = base64.b64encode(body_txt.encode()).decode()

    # combine the b64 header and body with a . seperator
    data = header_b64 + "." + body_b64

    # NaCl sign the data
    sig = signing_key.sign(data.encode('utf-8'), nacl.encoding.Base64Encoder)

    # append the signature
    data = data + "." + sig.signature.decode()

    return data


# function to generate OwnPush token for the data and send to the API
def sendpush(to, message):

    # generate the secure token
    token = generate_token("PRIVATE_API_KEY",
                           "PRIVATE_APP_KEY",
                           "PUBLIC_APP_KEY",
                           message,
                           to)

    data = {"token": token}

    # send token to the OwenPush send API
    r = requests.post('https://demo.ownpush.com/send', data=data, verify=False)
    return r.text
