#!/usr/bin/env python3

from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import tldextract
import argparse
import json


class Scanner:
    # Constructor
    def __init__(self, url: str, tag: str, payload: str, cookies: dict, proxy: str):
        self.target_url = url
        self.subdomains = []
        self.links_list = [url]
        self.tag = tag
        self.payload = payload
        self.cookies = cookies
        self.proxy = proxy

    # Get the entire page (including cookies etc.)
    def get_request(self, url):
        
        proxies = {
            "http": self.proxy,
            "https": self.proxy
        }
        try:
            return requests.get(self.add_http(url), cookies=self.cookies, proxies=proxies)
        except requests.exceptions.ConnectionError:
            pass
        except requests.exceptions.InvalidSchema:   # used when link leads to non-URL content (i.e. javascript: void(0))
            pass
        except requests.exceptions.MissingSchema:   # used when given path without domain, change to the target_url
            if url.startswith('/'):
                return requests.get(self.target_url + url, cookies=self.cookies, proxies=proxies)
            else:
                pass

    # find all tags in source code
    def extract_tag(self, url, tag="form"):       
        response = self.get_request(url)      
        parsed_html = BeautifulSoup(response.content, features="html.parser")   # response.content holds the source code of the URL
        tag_list = parsed_html.findAll(tag)
        return tag_list

    # find all input tags and insert a payload
    def submit_form(self, form, url, payload):
        action = form.get("action")
        method = form.get("method")
        input_list = form.findAll("input")
        post_url = urljoin(url, action)
        post_data = {}
        for i in input_list:
            name, _type, value = i.get("name"), i.get("type"), i.get("value")
            if _type == "text" or _type == "email" or _type == "password":
                post_data[name] = payload
            else:
                post_data[name] = value

        if method.lower() == "post":
            return requests.post(post_url, data=post_data)
        else:
            return requests.get(post_url, params=post_data)
    
    def add_http(self, url):
        return url if "http" in url else f"http://{url}"
    
    def strip_http(self, url: str):
        if "http://" in url:
            url = url.replace("http://", "")
        elif "https//" in url:
            url = url.replace("https://", "")
        return url if "www." not in url else url.replace("www.", "")
    
    def extract_subdomains(self, domain):
        f = open(f"{domain}.txt", "a")
        with open("./subdomains.txt", "r") as file:
            for line in file:
                line = line.strip() + "."
                subdomain = self.add_http(line + self.strip_http(self.target_url))
                try:
                    requests.get(subdomain)
                    self.subdomains.append(subdomain)
                    f.write(subdomain + "\n")
                except:
                    pass

    def extract_links(self, url):
        a_tag_list = self.extract_tag(url, "a")
        for a in a_tag_list:
            href = urljoin(self.target_url, a.get("href"))
            if tldextract.extract(href)[1] == tldextract.extract(self.target_url)[1]: # Limited to links in scope (domain)
                try:
                    if href not in self.links_list:
                        self.links_list.append(href)
                        print(href)
                        self.extract_links(href)
                except AttributeError:
                    continue
 
 
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crawl through a website and save all paths found, scan for any form and submit a user-given payload in every single one",
                                    epilog="Usage: python Scanner.py [-h] -u URL [-t TAG] [-p PAYLOAD] [-c COOKIES] [-x PROXY]")
    parser.add_argument("-u", "--url", type=str, help="The target URL", required=True)
    parser.add_argument("-t", "--tag", type=str, help="The tag to extract", default="form")
    parser.add_argument("-p", "--payload", type=str, help="The payload to submit", default="test")
    parser.add_argument("-c", "--cookies", type=json.loads, help='The cookies to use in requests, provide it in a dictionary format eg. -c \'{\\"cookie-name\\":\\"cookie-value\\"}\', default={}')
    parser.add_argument("-x", "--proxy", type=str, help="The proxy server to use")
    args = parser.parse_args()       
    scanner = Scanner(args.url, args.tag, args.payload, args.cookies, args.proxy)
    scanner.extract_links(args.url)