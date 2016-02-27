"""
    The MIT License (MIT)
    Copyright (c) 2016 Fastboot Mobile LLC.

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from project.models import PushDevice
from project.push.tasks import sendpush
import feedparser
import json
import threading


posted_items = {}

firstRun = True

def processFeed():

    global firstRun
    # Get the RSS feed
    feed = feedparser.parse('http://feeds.bbci.co.uk/news/world/rss.xml')
    print("loaded " + str(len(feed['entries'])) + " entries")

    # Load all push devices now
    devices = PushDevice.query.all()

    # get all feed entries
    entries = feed['entries']

    # iterate through the list
    for item in entries:
        item_flat = item['title']  # get the current title

        # check if we have posted the current title
        if item_flat not in posted_items:
            posted_items[item_flat] = item["link"]  # add the new item to the list of posted items
            print("added : " + item_flat + " || link : " + item["link"])  # debug log
            if not firstRun:
                for device in devices:
                    # Push new RSS entry to device if this isnt the first run
                    item_dict = {}
                    item_dict['title'] = item_flat  # add the title
                    item_dict['link'] = item["link"]  # add the http link
                    item_txt = json.dumps(item_dict)  # generate the JSON
                    print(sendpush(device.push_id, item_txt))  # Log and send the push notification

    firstRun = False
    threading.Timer(5, processFeed).start()
