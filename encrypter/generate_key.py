# use rsa to generate a pair of key
import rsa

KEY_SIZE = 2048

pubkey, privkey = rsa.newkeys(KEY_SIZE)
pub = pubkey.save_pkcs1()
pri = privkey.save_pkcs1()

with open("public.pem", "wb") as f:
    f.write(pub)

with open("private.pem", "wb") as f:
    f.write(pri)
