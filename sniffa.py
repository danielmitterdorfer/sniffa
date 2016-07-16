#!/usr/local/bin/python3

#
# Note: Ideally the shebang line would contain /usr/bin/env python3 instead of the
#       hardcoded path but it seems the user's environment is not inherited by
#       LaunchAgents (at least not on El Capitan).
#

import os
import sys
import errno
import json
import configparser
import urllib3
import urllib.parse
import datetime

import certifi
import pync

DOMAIN_SECTION_KEY = "sniffa.domain"


def ensure_dir(directory):
    try:
        os.makedirs(directory)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def creation_date(item):
    return datetime.datetime.strptime(item["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()


def main():
    if not len(sys.argv)  == 2:
        print("usage: %s domain_key" % sys.argv[0], file=sys.stderr)
        exit(1)
    
    domain_key = sys.argv[1]

    http = urllib3.PoolManager(cert_reqs="CERT_REQUIRED", ca_certs=certifi.where())

    watches_dir = "%s/.sniffa" % os.getenv("HOME")
    watches_file = "%s/watches-%s.ini" % (watches_dir, domain_key)

    ensure_dir(watches_dir)

    config = configparser.ConfigParser()
    config.read(watches_file)
    
    if not DOMAIN_SECTION_KEY in config or not "url" in config[DOMAIN_SECTION_KEY]:
        print("Invalid configuration in [%s]" % watches_file, file=sys.stderr)
        print("", file=sys.stderr)
        print("Please add a domain to query according to the following example in [%s]" % watches_file, file=sys.stderr)
        print("", file=sys.stderr)
        print("  [%s]" % DOMAIN_SECTION_KEY, file=sys.stderr)
        print("  url=https://discuss.example.org", file=sys.stderr)
        print("", file=sys.stderr)
        exit(1)

    domain = config[DOMAIN_SECTION_KEY]["url"]
    print("Checking for new posts on %s" % domain_key)
    
    for keyword in config.sections():
        if keyword == DOMAIN_SECTION_KEY:
            continue

        if "ids" in config[keyword]:
            ids = config[keyword]["ids"]
            if len(ids) > 0:
                known_ids = set([int(id) for id in config[keyword]["ids"].split(",")])
            else:
                known_ids = set()
        else:
            known_ids = set()

        query_string = urllib.parse.quote_plus("%s order:latest" % keyword)

        r = http.request("GET", "%s/search?q=%s" % (domain, query_string), headers={"Accept": "application/json"})
        results = json.loads(r.data.decode("utf-8"))

        topics_by_id = {}
        for topic in results["topics"]:
            topics_by_id[topic["id"]] = topic

        posts = []
        for post in results["posts"]:
            post_id = post["id"]
            if post_id not in known_ids:
                known_ids.add(post_id)
                posts.append(post)

        config[keyword]["ids"] = ",".join([str(id) for id in known_ids])

        sorted(posts, key=creation_date, reverse=True)

        for post in posts:
            topic = topics_by_id[post["topic_id"]]
            pync.Notifier.notify(topic["title"], title="New post mentioning '%s'" % keyword,
                                 open="%s/t/%s/%d" % (domain, topic["slug"], topic["id"]), group=str(topic["id"]))

    with open(watches_file, "w") as f:
        config.write(f)
    print("Finished")

if __name__ == "__main__":
    main()
