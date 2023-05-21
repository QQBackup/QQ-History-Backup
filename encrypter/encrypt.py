import os
import rsa
import sys

KEY_SIZE = 2048
PART_SIZE  = 245 # 2048 / 8 -11
ENCRYPTED_PART_SIZE = 256 # 2048 / 8
SUFFIX = ".enc"
DEC_SUFFIX = ".dec"

# https://www.cnblogs.com/sirxy/p/12141633.html
def encrypt(filename: str):
    with open("public.pem", mode="rb") as f_pub:
        pub = f_pub.read()
        public_key = rsa.PublicKey.load_pkcs1(pub)
    OUTPUT_FILENAME = filename + SUFFIX
    if os.path.isfile(OUTPUT_FILENAME):
        print(f"Output file {OUTPUT_FILENAME} already exists. Please delete it first.")
        return
    with open(filename, mode="rb") as file_in, open(OUTPUT_FILENAME, mode="wb") as file_out:
        while True:
            file_content = file_in.read(PART_SIZE)
            if not file_content:
                break
            else:
                message = file_content
                enc = rsa.encrypt(message, public_key)
                file_out.write(enc)
    print("finished. encrypted file is " + OUTPUT_FILENAME)

if len(sys.argv) == 2:
    filename = sys.argv[1]
else:
    raise ValueError("encrypt.py takes exactly 1 argument filename, but {} were given.".format(len(sys.argv) - 1))
encrypt(filename)
