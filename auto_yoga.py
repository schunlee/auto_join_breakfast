#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json

import datetime
import requests

import sys

reload(sys)
sys.setdefaultencoding("utf-8")

HEADERS = {"Accept": "application/json, text/plain, */*",
           "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36",
           "Content-Type": "application/json;charset=UTF-8",
           "APP_VERSION": "social_app_1.0"
           }
USER_NAME = "bill.li@nexa-corp.com"
PASSWORD = "shrinlee87885537"
LOCATION = "262adc8f-bad9-435a-8d8a-8fde521d68eb"

TARGETS = ["yoga", "瑜伽"]


def fetch_api_key():
    resp = requests.get("https://membersapi.wework.com/api/v10/login/key", headers=HEADERS).json()
    return resp["result"]["api_key"]


def login():
    # session = requests.Session()
    url = "https://auth.wework.com/api/sessions"
    payload = {"api_key": fetch_api_key(),
               "include_encrypted_user_uuid": True,
               "password": PASSWORD,
               "username": USER_NAME
               }
    resp = requests.post(url, data=json.dumps(payload), headers=HEADERS)
    if resp.status_code != 200:
        raise Exception("Login failed! - HTTP Code {}".format(resp.status_code))
    else:
        return resp.json()


def retrieve_events(encrypted_user_uuid):
    page = 1
    events_list = []
    while 1:
        print "Page: {}".format(page)
        params = {"encrypted_user_uuid": encrypted_user_uuid,
                  "index": "events",
                  "location_uuids": LOCATION,
                  "page": page,
                  "per_page": 10,
                  "types": "events",
                  "use_city": True
                  }
        resp = requests.get("https://membersapi.wework.com/api/v10/search", params=params, headers=HEADERS).json()
        return_data = resp["result"]["events"]["results"]
        if not len(return_data):
            return events_list
        events_list.extend(return_data)
        page += 1


def yoga_filter(resp):
    for target in TARGETS:
        resp = filter(lambda x: target in x["meta_data"]["event"]["name"].lower(), resp)
    return resp


def join_event(encrypted_user_uuid, user_uuid, event):
    if user_uuid in event["meta_data"]["event"]["attending"]:
        print "{}({}{}) ==> already attended".format(event["meta_data"]["event"]["name"],
                                                     event["meta_data"]["event"]["start_date"],
                                                     event["meta_data"]["event"]["time_string"])
        return
    resp = {"message": None}
    while not resp["message"]:
        params = {"encrypted_user_uuid": encrypted_user_uuid}
        resp = requests.post(
            "https://membersapi.wework.com/api/v4/events/{}/rsvp".format(event["meta_data"]["event"]["uuid"]),
            data=json.dumps({}), params=params, headers=HEADERS).json()
    else:
        print "{}({}{}) ==> ordered".format(event["meta_data"]["event"]["name"],
                                            event["meta_data"]["event"]["start_date"],
                                            event["meta_data"]["event"]["time_string"])


if __name__ == '__main__':
    pass
    print "----{}----".format(datetime.datetime.now())
    user_info = login()
    encrypted_user_uuid = user_info["result"]["session"]["encrypted_user_uuid"]
    user_uuid = user_info["result"]["session"]["user_uuid"]
    all_events = retrieve_events(encrypted_user_uuid)
    breakfast_events = yoga_filter(all_events)
    for _event in breakfast_events:
        join_event(encrypted_user_uuid, user_uuid, _event)
