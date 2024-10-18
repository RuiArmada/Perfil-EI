import pickle

class Payload:
    def __init__(self, data_dict:dict):
        for key in data_dict:
            setattr(self,key,data_dict[key])

    def __str__(self):
        strings = []
        for key in self.__dict__:
            atr = getattr(self,key)
            if type(atr) == str:
                strings.append(f'"{key}": "{getattr(self,key)}"')
            else:
                strings.append(f'"{key}": {getattr(self,key)}')

        return "{\"m:\"{" + ", ".join(strings) + "}}"

    def serialize(self):
        bits_n_bobs = []
        for key in self.__dict__:
            bits_n_bobs.append((key,getattr(self,key)))
        return pickle.dumps(bits_n_bobs)

    @staticmethod
    def deserialize(payload):
        try:
            # I wont validate the payload here, I will assume it is valid
            p = Payload({})
            data = pickle.loads(payload)
            for key,value in data:
                setattr(p,key,value)
            return p
        except Exception as e:
            return None



if __name__ == "__main__":
    payload = Payload({"sequence":1,"from_":"zephyrus","to_":"server", "a":"a_field","b":2,"c":3})
    print(payload)
    ser = payload.serialize()
    print(ser)
    size = len(ser)
    des = Payload.deserialize(ser)
    print(des)
