# data_store.py
data_store = {}

def store_data(iid, value):
    keys = iid.split('.')
    d = data_store
    for key in keys[:-1]:
        if key not in d:
            d[key] = {}
        d = d[key]
    d[keys[-1]] = value
    return True

def retrieve_data(iid):
    keys = iid.split('.')
    d = data_store
    for key in keys:
        if key in d:
            d = d[key]
        else:
            return None
    return d  # Return the final value directly, assuming it is stored correctly

def store_error(error):
    print(f"Error: {error}")
