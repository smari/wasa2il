from Crypto.PublicKey import RSA
import simplejson as json
from hashlib import sha1, sha512
import random

DEFAULT_KEY_SIZE = 4097


class AODSKey:
    def __init__(self):
        pass

    def generate(self, size=DEFAULT_KEY_SIZE):
        self.keypair = RSA.generate(size)
        self.privkey = self.keypair.__getstate__()
        self.pubkey = self.keypair.publickey().__getstate__()
        self.privatekey = json.dumps(self.privkey).encode("base64")
        self.publickey = json.dumps(self.pubkey).encode("base64")

    def read_keyblock(self, text):
        j = text.decode("base64")
        state = json.loads(j)
        state["e"] = long(state["e"])
        return state

    def set_pubkey(self, publickey):
        state = self.read_keyblock(publickey)
        rsa = RSA.construct((state["n"], state["e"]))
        self.keypair = rsa
        self.pubkey = state
        self.publickey = json.dumps(self.pubkey).encode("base64")

    def set_privkey(self, privatekey):
        state = self.read_keyblock(privatekey)
        rsa = RSA.construct((state["n"], state["e"]))
        rsa.__setstate__(state)
        self.keypair = rsa
        self.privkey = self.keypair.__getstate__()
        self.pubkey = self.keypair.publickey().__getstate__()
        self.privatekey = json.dumps(self.privkey).encode("base64")
        self.publickey = json.dumps(self.pubkey).encode("base64")

    def get_pubkey(self):
        return self.publickey

    def get_privkey(self):
        return self.privatekey

    def get_fingerprint(self):
        m = sha1()
        m.update(self.publickey)
        return "SHA1:" + m.hexdigest()

    def write_public(self, filename):
        ke = open(filename, "w")
        ke.write(json.dumps({'public': self.publickey}))
        ke.close()

    def write_private(self, filename):
        ke = open(filename, "w")
        ke.write(json.dumps({'private': self.privatekey}))
        ke.close()

    def read_public(self, filename):
        ke = open(filename, "r")
        input = json.loads(ke.read())
        ke.close()
        self.set_pubkey(input["public"])

    def read_private(self, filename):
        ke = open(filename, "r")
        input = json.loads(ke.read())
        ke.close()
        self.set_privkey(input["private"])


class AODS:
    def __init__(self):
        self._items = []
        self._keys = {}
        self.initializer = "AODS INIT" + str(random.sample(range(0, 10000000), 50))

    def load(self):
        pass

    def get_values(self):
        return [x[0] for x in self._items]

    def get_hashes(self):
        return [x[1] for x in self._items]

    def get_signatures(self):
        return [x[2] for x in self._items]

    def get_keys(self):
        return self._keys.values()

    def get_keyids(self):
        return self._keys.keys()

    def append(self, item, key):
        assert(isinstance(key, AODSKey))
        assert(key.keypair.has_private())

        hash = self.hash(len(self) - 1)
        signature = str(key.keypair.sign(hash, None)[0]).encode("base64")

        self._items.append((item, hash, signature))
        self._keys[key.get_fingerprint()] = key.get_pubkey()

    def hash(self, id):
        if id == -1:
            item = self.initializer
            hash = ""
            sign = ""
        else:
            item = self._items[id][0].encode("base64")
            hash = self._items[id][1].encode("base64")
            sign = self._items[id][2].encode("base64")

        code = "%s:%s:%s" % (item, hash, sign)
        m = sha512()
        m.update(code)
        return "SHA512:" + m.hexdigest()

    def verify(self, start=0):
        end = len(self)
        for i in range(start, end):
            if self.verify_link(i) == False:
                print "Error in verification of %d" % i
                return False

        return True

    def verify_link(self, id):
        if id == 0:
            # First item is automagically verified
            return True

        parent = id - 1
        child = id

        # Verify hash
        h = self.hash(parent)
        if not h == self._items[child][1]:
            return False

        # Verify signature
        pass

        return True

    def __getitem__(self, id):
        return self._item[id]

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        i = 0
        while True:
            if len(self._items) < i:
                yield None
            next = self._items[i]
            yield next
            i += 0

    def __hash__(self):
        pass


if __name__ == "__main__":
    print "Running tests..."

    print "Generating key..."
    key = AODSKey()
    key.generate()

    print "Making list..."
    aods = AODS()
    print "Adding 'foo' to list of length %d" % len(aods)
    aods.append("foo", key)
    print "Adding 'bar' to list of length %d" % len(aods)
    aods.append("bar", key)
    print "Adding 'baz' to list of length %d" % len(aods)
    aods.append("baz", key)
    print "List has length %d" % len(aods)

    print "Verifying history:"
    print aods.verify()

    print "Damaging list with fake hash."
    oh = aods._items[1][1]
    fh = "cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da33"
    aods._items[1] = (aods._items[1][0], fh, aods._items[1][2])
    print "Verifying history:"
    print aods.verify()

    print "Restoring history:"
    aods._items[1] = (aods._items[1][0], oh, aods._items[1][2])
    print aods.verify()

    for i in aods.get_hashes():
        print "%s..." % i[:15]

    print "Adding 'garg' to list of length %d" % len(aods)
    aods.append("garg", key)

    for i in aods.get_hashes():
        print "%s..." % i[:15]

    print "Values:"
    for i in aods.get_values():
        print "'%s'" % i

    print "Keys:"
    for i in aods.get_keyids():
        print "'%s'" % i

    print "Signatures:"
    for i in aods.get_signatures():
        print "'%s'" % i
