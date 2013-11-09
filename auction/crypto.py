import datetime
import gnupg
import tempfile

class Crypto():
    def __init__(self, homedir=None):
        homedir = homedir or tempfile.mkdtemp()
        # TODO(zjn): don't specify the binary
        self.gpg = gnupg.GPG(homedir=homedir, binary='gpg2')

    def gen_key(self):
        tomorrow = datetime.datetime.now() + datetime.timedelta(days=2)
        gen_key_params = {
                'name_comment': 'SilentAuction: Me',
                'key_type': 'ELG-E',
                'expire_date': datetime.datetime.strftime(tomorrow, '%Y-%m-%d'),
                'key_length': 4096,
                'key_usage': 'encrypt',
                'testing': True #TODO(zjn): really you should get rid of this
            }
        gen_key_input = self.gpg.gen_key_input(**gen_key_params)
        self.my_key = self.gpg.gen_key(gen_key_input)

    def export_key(self):
        return self.gpg.export_keys(self.my_key.fingerprint)

    def import_key(self, key):
        return self.gpg.import_keys(key).fingerprints[0]

    def encrypt(self, message, key):
        return self.gpg.encrypt(message, key.fingerprint).data

    def decrypt(self, ciphertext):
        return self.gpg.decrypt(ciphertext).data

    def __del__(self):
        pass
        #TODO(zjn): clean up tmpdir

