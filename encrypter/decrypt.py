import os
import rsa
import sys

if not os.path.isfile("private.pem"):
    print("use encrypt.py to encrypt a file.")
    exit()

KEY_SIZE = 2048
PART_SIZE  = 245 # 2048 / 8 -11
ENCRYPTED_PART_SIZE = 256 # 2048 / 8
SUFFIX = ".enc"
DEC_SUFFIX = ".dec"

# https://www.cnblogs.com/sirxy/p/12141633.html
def decrypt(filename: str):
    with open("private.pem", mode="rb") as f_priv:
        priv = f_priv.read()
        private_key = rsa.PrivateKey.load_pkcs1(priv)
    OUTPUT_FILENAME = filename.removesuffix(SUFFIX) + DEC_SUFFIX
    if os.path.isfile(OUTPUT_FILENAME):
        print(f"Output file {OUTPUT_FILENAME} already exists. Please delete it first.")
        return
    with open(filename, mode="rb") as file_in, open(OUTPUT_FILENAME, mode="wb") as file_out:
        while True:
            file_content = file_in.read(ENCRYPTED_PART_SIZE)
            if not file_content:
                break
            if len(file_content) != ENCRYPTED_PART_SIZE:
                raise ValueError(f"file_content length (extra {len(file_content)}) is not ENCRYPTED_PART_SIZE ({ENCRYPTED_PART_SIZE})!")
            else:
                message = file_content
                enc = rsa.decrypt(message, private_key)
                file_out.write(enc)
    print("finished. decrypted file is " + OUTPUT_FILENAME)

if len(sys.argv) == 2:
    filename = sys.argv[1]
else:
    raise ValueError("decrypt.py takes exactly 1 argument filename, but {} were given.".format(len(sys.argv) - 1))
decrypt(filename)
