#!/usr/bin/env python3

# Creates a socvr report with all unhandled Natty reports and maintains an ignore list

import requests
import json as js
import webbrowser
from random import randrange
from argparse import ArgumentParser
from math import ceil
import shelve

MS_KEY = "f6e2b03cd2dcae440f61a2e896acc8d89b5a3da0a4d9f87ec7711b0650ecd967"
POSTS_FILTER = "HKMJOLHGHMKNOGFGFINLMFLONHKFHJ"
REASONS_FILTER = "GFLHKIHJKNLJKLMFGMIFNGL"

socvrAPI = 'http://reports.socvr.org/api/create-report'

def _pluralize(word, amount):
    return word if amount == 1 else word + 's'

def _getData():
    remote = requests.get("https://metasmoke.erwaysoftware.com/api/v2.0/posts",
                          params={"key": MS_KEY, "filter": POSTS_FILTER, "page": 1, "per_page": 100})
    remote.raise_for_status()

    data = remote.json()
    reports = []

    for data in data['items']:
        if not (data['is_fp'] or data['is_naa'] or (data['is_tp'] and (data['revision_count'] or data['deleted_at']))):
            reports.append(data)

    return reports


def _buildReport(reports):
    ret = {'botName' : 'OpenReportsScript'}
    posts = []

    for v in reports:
        remote = requests.get("https://metasmoke.erwaysoftware.com/api/v2.0/posts/%d/reasons" % v['id'],
                              params={"key": MS_KEY, "filter": REASONS_FILTER})
        remote.raise_for_status()

        reason_list = remote.json()["items"]

        reasons = ', '.join(r['reason_name'] for r in reason_list)
        score = sum(r['weight'] for r in reason_list)

        posts.append([{'id':'title', 'name': v['title'], 'value':v['link'], 'specialType':'link'},
            {'id':'score', 'name':'Autoflag Weight', 'value':score},
            {'id':'reasons', 'name':'Reasons', 'value':reasons}])

    ret['posts'] = posts
    return ret

def OpenLinks(reports):
    if len(reports) == 0:
        return None
    report = _buildReport(reports)
    
    r = requests.post(socvrAPI, data=js.dumps(report))
    r.raise_for_status()
    return r.text

def OpenReports(mode, user, client, amount=None, back=False):
    userID = user.id

    filename = str(userID) + client.host + '.ignorelist'
    curr = _getData()

    with shelve.open(filename) as db:
        try:
            ignored = db['ignored']
            last = db['last']
        except:
            ignored = []
            last = []

        if mode == 'ignore_rest':
            newIgnored = [v['id'] for v in last if v in curr]
            db['ignored'] = newIgnored
            db['last'] = last
            msg = str(len(newIgnored)) + ' %s in ignore list.'%_pluralize('report', len(newIgnored))
            return msg
        else:
            msg = ''

            good = [v for v in curr if not v['id'] in ignored]
            numIgnored = len(curr) - len(good)

            if mode == 'fetch_amount':
                if len(curr) == 0:
                    msg += 'All reports have been tended to.'
                else:
                    msg += 'There ' + ('is ' if len(curr) == 1 else 'are ') + str(len(curr)) \
                            + ' unhandled ' + ('report' if len(curr) == 1 else 'reports') \
                            + ', %s of which '%numIgnored \
                            + ('is' if numIgnored == 1 else 'are') + ' on your ignore list.'
                return msg
            else:
                if amount:
                    if not back:
                        good = good[:amount]
                    elif amount < len(good):
                        good = good[len(good) - amount:]
                goodIds = [v['id'] for v in good]
                last = [v for v in curr if (v['id'] in goodIds) or (v['id'] in ignored)]

                db['last'] = last
                db['ignored'] = ignored
                if numIgnored:
                    msg += 'Skipped %s ignored %s. '%(numIgnored, _pluralize('report', numIgnored))
                report = OpenLinks(good)
                if not good:
                    msg += 'All reports have been tended to.'
                else:
                    msg += 'Opened %s [report%s](%s).'%(len(good),'' if len(good) == 1 else 's', report)
                return msg

