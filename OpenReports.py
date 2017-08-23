#!/usr/bin/env python3

# Creates a socvr report with all unhandled Natty reports and maintains an ignore list

import requests
import json as js
import webbrowser
from random import randrange
from argparse import ArgumentParser
from math import ceil

apiUrl = 'http://reports.socvr.org/api/create-report'
seApiUrl = 'https://api.stackexchange.com/2.2/posts/'

def _pluralize(word, amount):
    return word if amount == 1 else word + 's'

def _getData():
    remote = requests.get('http://samserver.bhargavrao.com:8000/napi/api/reports/all')
    remote.raise_for_status()

    data = js.loads(remote.text)
    return data['items']

def _buildReport(reports):
    ret = {'botName' : 'OpenReportsScript'}
    posts = []
    for v in reports:
        reasons = ', '.join(r['reasonName'] for r in v['reasons'])
        posts.append([{'id':'title', 'name':v['name'], 'value':v['link'], 'specialType':'link'},
            {'id':'score', 'name':'NAA Score', 'value':v['naaValue']},
            {'id':'reasons', 'name':'Reasons', 'value':reasons}])
    ret['posts'] = posts
    return ret

def OpenLinks(reports):
    if len(reports) == 0:
        return None
    report = _buildReport(reports)
    
    r = requests.post(apiUrl, data=js.dumps(report))
    r.raise_for_status()
    return r.text

def OpenReports(mode='normal', userID, amount=None, back=False,
        lowRep=False):
    filename = str(userID) + '.ignorelist'
    reports = _getData()
    curr = [v['name'] for v in reports]

    try:
        dataFile = open(filename)
        ignored = [v for v in dataFile.readline().split()]
        last = [v for v in dataFile.readline().split()]
        dataFile.close()
    except:
        ignored = []
        last = []

    if mode == 'ignore_rest':
        newIgnored = [v for v in last if v in curr]
        f = open(filename, 'w')
        f.write(' '.join(newIgnored))
        f.write('\n')
        f.write(' '.join(last))
        msg = str(len(newIgnored)) + ' %s in ignore list.'%_pluralize('report', len(newIgnored))
        return msg
    else:
        msg = ''
        if lowRep:
            nonDeleted = []
            for i in range(ceil(len(curr) / 100)):
                r = requests.get(seApiUrl + ';'.join(curr[i*100:(i+1)*100]) + '?site=stackoverflow&key=Vhtdwbqa)4HYdpgQlVMqTw((')
                r.raise_for_status()
                data = js.loads(r.text)
                nonDeleted += [str(v['post_id']) for v in data['items']]
            numDel = len(curr) - len(nonDeleted)
            if numDel:
                plopper = randrange(100)
                plopStr = 'plop' if plopper == 0 else 'pleb'
                msg += 'Ignored %s deleted %s (<10k '%(numDel, _pluralize('post', numDel)) \
                        + plopStr + '). '
            curr = nonDeleted
            reports = [v for v in reports if v['name'] in curr]
        good = [v for v in reports if not v['name'] in ignored]
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
            f = open(filename, 'w')
            f.write(' '.join(ignored))
            f.write('\n')
            goodIds = [v['name'] for v in good]
            f.write(' '.join([v for v in curr if (v in goodIds) or (v in ignored)]))
            if numIgnored:
                msg += 'Skipped %s ignored %s. '%(numIgnored, _pluralize('report', numIgnored))
            report = OpenLinks(good)
            if not good:
                msg += 'All reports have been tended to.'
            else:
                msg += 'Opened %s [report%s](%s).'%(len(good),'' if len(good) == 1 else 's', report)
            return msg

