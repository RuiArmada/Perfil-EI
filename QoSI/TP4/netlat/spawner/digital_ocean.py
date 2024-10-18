import os
import secrets
import json
import random
import subprocess

WORDS = ["I", "took", "a", "walk", "around", "the", "world", "to", "ease", "my", "troubled", "mind","I", "left", "my", "body", "lying", "somewhere", "in", "the", "sands", "of", "time","I", "watched", "the", "world", "float", "to", "the", "dark", "side", "of", "the", "moon","I", "feel", "there-s", "nothing", "I", "can", "do", "yeah","I", "watched", "the", "world", "float", "to", "the", "dark", "side", "of", "the", "moon","After", "all", "I", "knew", "it", "had", "to", "be", "something", "to", "do", "with", "you","I", "really", "don-t", "mind", "what", "happens", "now", "and", "then","As", "long", "as", "you-ll", "be", "my", "friend", "at", "the", "end","If", "I", "go", "crazy", "then", "will", "you", "still", "call", "me", "Superman","If", "I-m", "alive", "and", "well", "will", "you", "be", "there", "holding", "my", "hand","I-ll", "keep", "you", "by", "my", "side", "with", "my", "superhuman", "might","Kryptonite","You", "called", "me", "strong", "you", "called", "me", "weak","But", "still", "your", "secrets", "I", "will", "keep","You", "took", "for", "granted", "all", "the", "times", "I", "never", "let", "you", "down","You", "stumbled", "in", "and", "bumped", "your", "head", "If", "not", "for", "me", "then", "you-d", "be", "dead","I", "picked", "you", "up", "and", "put", "you", "back", "on", "solid", "ground", "If", "I", "go", "crazy", "then", "will", "you", "still", "call", "me", "Superman","If", "I-m", "alive", "and", "well", "will", "you", "be", "there", "holding", "my", "hand","I-ll", "keep", "you", "by", "my", "side", "with", "my", "superhuman", "might","Kryptonite","Oh", "no","no","no","no","no", "If", "I", "go", "crazy", "then", "will", "you", "still", "call", "me", "Superman","If", "I-m", "alive", "and", "well", "will", "you", "be", "there", "holding", "my", "hand","I-ll", "keep", "you", "by", "my", "side", "with", "my", "superhuman", "might","Kryptonite", "yea", "If", "I", "go", "crazy", "then", "will", "you", "still", "call", "me", "Superman","If", "I-m", "alive", "and", "well", "will", "you", "be", "there", "holding", "my", "hand","I-ll", "keep", "you", "by", "my", "side", "with", "my", "superhuman", "might","Kryptonite","Oh", "whoa","whoa","Oh", "whoa","whoa","Oh", "whoa","whoa"]

def random_word():
    return random.choice(WORDS)
    
def __password__(length=16):
    return secrets.token_urlsafe(length)

def __name__(region: str, machine: str):
    random = random_word()
    return f'netlat-{__password__(4).replace("_","0")}-{random}-{region}-{machine}'

class DigitalOceanSpawner():
    def __init__(self, config_path: str, debug = False) -> None:
        self.debug = debug
        self.config = json.load(open(config_path))
        self.droplets = []
        image = self.config['image']
        size = self.config['size']
        ssh_keys = self.config['ssh-keys']
        user_data = self.config['user-data']
        for region in self.config['regions']:
            drop = Droplet(__name__(region, image),region, size, image, ssh_keys, user_data)
    
            state = drop.create()
            if state:
                self.droplets.append(drop)
                if self.debug:
                    print(f'{drop.name} created successfully')
            else:
                if self.debug:
                    print(f'{drop.name} failed to create')
            ## Stupid way of generating only one droplet for debugging
            if self.debug and state:
                break
    def destroy(self):
        for drop in self.droplets:
            state = drop.destroy()
            if state:
                if self.debug:
                    print(f'{drop.name} destroyed successfully')
            else:
                if self.debug:
                    print(f'{drop.name} failed to destroy')


class Droplet:
    def __init__(self, name, region: str, size: str, image: str, ssh_keys: list, user_data: str) -> None:
        self.tag = 'netlat'
        self.name = name
        self.region = region
        self.size = size
        self.image = image
        self.ssh_keys = ssh_keys
        self.password = __password__()
        self.user_data = user_data

    def __str__(self) -> str:
        string = f'Droplet {self.name}:\n\tRegion: {self.region}\n\tSize: {self.size}\n\tImage: {self.image}\n\tSSH Keys: {self.ssh_keys}\n\tPassword: {self.password}\n\tUser Data: {self.user_data}'
        return string

    def __repr__(self) -> str:
        return self.__str__()
    
    def create(self):
        out = False
        result = subprocess.run(f'doctl compute droplet create {self.name} --region {self.region} --size {self.size} --image {self.image} --ssh-keys {self.ssh_keys} --user-data-file {self.user_data} --tag-name {self.tag} --wait',shell=True)
        if result.returncode == 0:
            out = True
        return out
    
    def destroy(self):
        out = False
        result = subprocess.run(f'doctl compute droplet delete {self.name} --force',shell=True)
        if result.returncode == 0:
            out = True
        return out
    
