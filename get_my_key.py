import hashlib, hmac, ecdsa
from mnemonic import Mnemonic
from Crypto.Hash import keccak

def derive_eth_address(pk_bytes):
    sk = ecdsa.SigningKey.from_string(pk_bytes, curve=ecdsa.SECP256k1)
    vk = sk.get_verifying_key().to_string("uncompressed")[1:]
    k = keccak.new(digest_bits=256).update(vk).digest()
    return "0x" + k[-20:].hex()

def get_eth_child(seed, index):
    I = hmac.new(b"Bitcoin seed", seed, hashlib.sha512).digest()
    k, cc = I[:32], I[32:]
    for i in [44, 60, 0]:
        data = b'\x00' + k + (i + 0x80000000).to_bytes(4, 'big')
        I = hmac.new(cc, data, hashlib.sha512).digest()
        k, cc = I[:32], I[32:]
    for i in [0, index]:
        data = b'\x00' + k + i.to_bytes(4, 'big')
        I = hmac.new(cc, data, hashlib.sha512).digest()
        k, cc = I[:32], I[32:]
    return k

# TÄSSÄ ON SE PAPERIN SANALISTA
words = "sheriff eight anchor scare silk trial goddess grant truly notable hen inspire"
seed = Mnemonic.to_seed(words)

print("\n🔍 ETSITÄÄN OSOITETTA 0xBbAd...")
print("-" * 50)

for i in range(10):
    pk = get_eth_child(seed, i)
    addr = derive_eth_address(pk)
    print(f"Index {i} | Address: {addr}")
    if addr.lower().startswith("0xbbad"):
        print(f"\n✅ LÖYTYI!")
        print(f"🔑 Private Key: {pk.hex()}")
        break
    print("-" * 30)
