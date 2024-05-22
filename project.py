import feedparser
import string
import time
import threading
from project_util import translate_html
from mtTkinter import *
from datetime import datetime

#======================
# Code for retrieving and parsing
# Google and Yahoo News feeds
#======================

def process(url):
    """
    Fetches news items from the rss url and parses them.
    Returns a list of NewsStory instances.
    """
    feed = feedparser.parse(url)
    entries = feed.entries
    ret = []
    
    for entry in entries:
        guid = entry.get('guid', 'No GUID')
        title = translate_html(entry.get('title', 'No Title'))
        link = entry.get('link', 'No Link')
        description = translate_html(entry.get('description', 'No Description'))
        
        # Parsing pubdate
        if 'published' in entry:
            pubdate_str = entry.published
            try:
                pubdate = datetime.strptime(pubdate_str, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                pubdate = datetime.strptime(pubdate_str, "%a, %d %b %Y %H:%M:%S %Z")
        else:
            pubdate = datetime.now()  # Use current time if pubdate is not available
        
        newsStory = NewsStory(guid, title, description, link, pubdate)
        ret.append(newsStory)
    
    return ret

#======================
# Data structure design
#======================
# Problem 1
class NewsStory:
    def __init__(self, guid, title, description, link, pubdate):
        self.guid = guid
        self.title = title
        self.description = description
        self.link = link
        self.pubdate = pubdate
    
    def get_guid(self):
        return self.guid
    
    def get_title(self):
        return self.title
    
    def get_description(self):
        return self.description
    
    def get_link(self):
        return self.link
    
    def get_pubdate(self):
        return self.pubdate

#======================
# Triggers
#======================

class Trigger(object):
    def evaluate(self, story):
        """
        Returns True if an alert should be generated
        for the given news item, or False otherwise.
        """
        # DO NOT CHANGE THIS!
        raise NotImplementedError

# PHRASE TRIGGERS
# Problem 2
# TODO: PhraseTrigger
class PhraseTrigger(Trigger):
    def __init__(self, phrase):
        self.phrase = phrase.lower()
    
    def is_phrase_in(self, text):
        text = text.lower()
        for char in string.punctuation:
            text = text.replace(char, ' ')
        text_words = text.split()
        phrase_words = self.phrase.split()
        for i in range(len(text_words) - len(phrase_words) + 1):
            if text_words[i:i + len(phrase_words)] == phrase_words:
                return True
        return False
# Problem 3
# TODO: TitleTrigger
class TitleTrigger(PhraseTrigger):
    def evaluate(self, story):
        return self.is_phrase_in(story.get_title())
# Problem 4
# TODO: DescriptionTrigger
class DescriptionTrigger(PhraseTrigger):
    def evaluate(self, story):
        return self.is_phrase_in(story.get_description())

# TIME TRIGGERS
# Problem 5
# TODO: TimeTrigger
# Constructor:
#        Input: Time has to be in EST and in the format of "%d %b %Y %H:%M:%S".
#        Convert time from string to a datetime before saving it as an attribute.
class TimeTrigger(Trigger):
    def __init__(self, time):
        self.time = datetime.strptime(time, "%d %b %Y %H:%M:%S")
# Problem 6
# TODO: BeforeTrigger and AfterTrigger
class BeforeTrigger(TimeTrigger):
    def evaluate(self, story):
        return story.get_pubdate() < self.time

class AfterTrigger(TimeTrigger):
    def evaluate(self, story):
        return story.get_pubdate() > self.time

# COMPOSITE TRIGGERS
# Problem 7
# TODO: NotTrigger

class NotTrigger(Trigger):
    def __init__(self, trigger):
        self.trigger = trigger
    
    def evaluate(self, story):
        return not self.trigger.evaluate(story)
# Problem 8
# TODO: AndTrigger
class AndTrigger(Trigger):
    def __init__(self, trigger1, trigger2):
        self.trigger1 = trigger1
        self.trigger2 = trigger2
    
    def evaluate(self, story):
        return self.trigger1.evaluate(story) and self.trigger2.evaluate(story)
# Problem 9
# TODO: OrTrigger

class OrTrigger(Trigger):
    def __init__(self, trigger1, trigger2):
        self.trigger1 = trigger1
        self.trigger2 = trigger2
    
    def evaluate(self, story):
        return self.trigger1.evaluate(story) or self.trigger2.evaluate(story)

#======================
# Filtering
#======================
# Problem 10
def filter_stories(stories, triggerlist):
    """
    Takes in a list of NewsStory instances.
    Returns a list of only the stories for which a trigger in triggerlist fires.
    """
    # TODO: Problem 10
    # This is a placeholder
    # (we're just returning all the stories, with no filtering)
    filtered_stories = []
    
    for story in stories:
        for trigger in triggerlist:
            if trigger.evaluate(story):
                filtered_stories.append(story)
                break
    
    return filtered_stories

#======================
# User-Specified Triggers
#======================
# Problem 11
def read_trigger_config(filename):
    """
    filename: the name of a trigger configuration file
    Returns: a list of trigger objects specified by the trigger configuration file.
    """
      # We give you the code to read in the file and eliminate blank lines and
    # comments. You don't need to know how it works for now!
    trigger_file = open(filename, 'r')
    lines = [line.strip() for line in trigger_file.readlines() if line.strip() and not line.strip().startswith('//')]
    trigger_file.close()
    
    triggers = {}
    trigger_list = []
    
    for line in lines:
        parts = line.split(',')
        if parts[0] == 'ADD':
            for name in parts[1:]:
                if name in triggers:
                    trigger_list.append(triggers[name])
        else:
            trigger_name = parts[0]
            trigger_type = parts[1]
            if trigger_type == 'TITLE':
                triggers[trigger_name] = TitleTrigger(parts[2])
            elif trigger_type == 'DESCRIPTION':
                triggers[trigger_name] = DescriptionTrigger(parts[2])
            elif trigger_type == 'AFTER':
                triggers[trigger_name] = AfterTrigger(parts[2])
            elif trigger_type == 'BEFORE':
                triggers[trigger_name] = BeforeTrigger(parts[2])
            elif trigger_type == 'NOT':
                if parts[2] in triggers:
                    triggers[trigger_name] = NotTrigger(triggers[parts[2]])
            elif trigger_type == 'AND':
                if parts[2] in triggers and parts[3] in triggers:
                    triggers[trigger_name] = AndTrigger(triggers[parts[2]], triggers[parts[3]])
            elif trigger_type == 'OR':
                if parts[2] in triggers and parts[3] in triggers:
                    triggers[trigger_name] = OrTrigger(triggers[parts[2]], triggers[parts[3]])
    
    return trigger_list

#======================
# Main Execution
#======================

SLEEPTIME = 120  # seconds

def main_thread(master):
        # A sample trigger list - you might need to change the phrases to correspond
    # to what is currently in the news
    try:
        triggerlist = read_trigger_config('triggers.txt')
        
        frame = Frame(master)
        frame.pack(side=BOTTOM)
        scrollbar = Scrollbar(master)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        title = StringVar()
        title.set("Google & Yahoo Top News")
        ttl = Label(master, textvariable=title, font=("Helvetica", 18))
        ttl.pack(side=TOP)
        
        cont = Text(master, font=("Helvetica", 14), yscrollcommand=scrollbar.set)
        cont.pack(side=BOTTOM)
        cont.tag_config("title", justify='center')
        
        button = Button(frame, text="Exit", command=master.destroy)
        button.pack(side=BOTTOM)
        
        guidShown = set()
        
        def get_cont(newstory):
            if newstory.get_guid() not in guidShown:
                cont.insert(END, newstory.get_title() + "\n", "title")
                cont.insert(END, "\n---------------------------------------------------------------\n", "title")
                cont.insert(END, newstory.get_description() + "\n")
                cont.insert(END, "\n*\n", "title")
                guidShown.add(newstory.get_guid())
        
        while True:
            print("Polling...")
            stories = process("http://news.google.com/news?output=rss")
            stories.extend(process("http://news.yahoo.com/rss/topstories"))
            
            filtered_stories = filter_stories(stories, triggerlist)
            
            for story in filtered_stories:
                get_cont(story)
            
            scrollbar.config(command=cont.yview)
            
            print(f"Sleeping for {SLEEPTIME} seconds...")
            time.sleep(SLEEPTIME)
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    root = Tk()
    root.title("RSS Feed Parser")
    t = threading.Thread(target=main_thread, args=(root,))
    t.start()
    root.mainloop()
