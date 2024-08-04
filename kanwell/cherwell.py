from cherpy import config_from_env
from cherpy.main import search_object,get_object_schema,extract_data,update_object_from_file
from cherpy.main import save_objects
import pprint
class Fields(object):
    def __init__(self, field_dict,record):
        self.__dict__['field_dict'] = field_dict
        self.__dict__['record'] = record
    def __getattr__(self, item):
        for field in self.__dict__['field_dict']:

            if field['name'].lower() == item.lower():
                return field['value']

    def __setattr__(self, key, value):
        for field in self.__dict__['field_dict']:
            if field['name'].lower() == key.lower():
                field['value'] = value
                field['dirty'] = True
                self.__dict__['record']._object_dict['persist'] = True

    # def mark_dirty(self):
    #     for field in self.__dict__['field_dict']:
    #         field['dirty'] = True
    # def __str__(self):
    #     return [row['name'] for row in self._field_dict]

class CherwellRecord(object):
    def __init__(self, object_dict):
        self._object_dict = object_dict
        self.field = Fields(object_dict['fields'],self)

    def fields(self):
        return [f['name'] for f in self._object_dict['fields']]

    def __getattr__(self, item):
        if item not in self._object_dict:
            return self.field.__getattr__(item)
        return self._object_dict[item]

#usage example
#c = CherwellRecord(object)
#print(c.field.summary)

def update_records(update_records):
    client = config_from_env('cherpy_dev')
    client.login()
    if type (update_records) != list:
        udpates = [update_records._object_dict]
    else:
        udpates = [u._object_dict for u in update_records]
    save_objects(client,{'saveRequests':udpates})


def load_records():
    client = config_from_env('cherpy_dev')
    client.login()
    s=search_object(client, object_name='Enhancement', fields=['Summary','name','ownedbyteam', 'status'],pageSize=100)
    records = [CherwellRecord(row) for row in s.json()['businessObjects']]

    return records

if __name__ == '__main__':
    client = config_from_env('cherpy_dev')
    client.login()
    records = load_records()

