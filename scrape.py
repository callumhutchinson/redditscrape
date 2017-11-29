import praw
import bs4 as bs
import urllib2
import time
import datetime
import matplotlib.pyplot as plt
import pandas as pd
import time,sys

#lists to store data
subred_name = []
users_online = []
post_title = []
post_made = []
net_votes = []
up_ratio = []

#dictionary to store scraped data
scraped_data = {'subreddit_name' : subred_name, 
				'users_online' : users_online,
				'post_made_hrs' : post_made,
				'net_votes' : net_votes,
				'up_ratio' : up_ratio}

#create a BeautifulSoup object from the source code
hdr = { 'User-Agent' : 'rankingproject' }
req = urllib2.Request("https://www.reddit.com", headers=hdr)
source = urllib2.urlopen(req).read()
soup = bs.BeautifulSoup(source, 'lxml')


#list of top 5 subreddits
topreddits = []
#gets the top 5 subreddits
for headers in soup.find_all('a')[5:10]:
	topreddits.append(headers.string)

#rectifies some unicode printing of subreddit names
topreddits = [str(topreddits[x]) for x in range(len(topreddits))]

#fix for changing of index when pulling top subreddits
#if the index changes causing first subreddit to be 'users' 
#clear list and start from position 6
if (topreddits[0] == 'users'):
	topreddits=[]
	for headers in soup.find_all('a')[6:11]:
		topreddits.append(headers.string)

topreddits = [str(topreddits[x]) for x in range(len(topreddits))]

print "Top 5 subreddits at", time.ctime(), ":\n"
print topreddits

#create a read only reddit instance
reddit = praw.Reddit(client_id='ah3BLZiKZZVMIQ',
                     client_secret='0e8HB2IAg4lcDOkInk6ohtgqj58',
                     user_agent='rankingproject')

#get time since post
def get_time_since_posted(submission):
	time = datetime.datetime.utcfromtimestamp(submission.created_utc)
	now = datetime.datetime.utcnow()
	return datetime.timedelta.total_seconds(now - time)/(60*60)

#total users online is a list, converts to int
def list_to_int(in_list):
	time_int = ""
	for i in in_list:
		if (i != ","):
			time_int += i
	return int(time_int)

#go into each subreddit and pull info

for subred in topreddits:
	print "Scraping ",subred,"..."
	#gets number of people on the subreddit
	sub_url = "https://www.reddit.com/r/" + subred
	req = urllib2.Request(sub_url, headers=hdr)
	source = urllib2.urlopen(req).read()
	soup = bs.BeautifulSoup(source, 'lxml')
	#appends the number of users online now
	time_str = soup.find("p", class_="users-online").find("span",class_="number").string
	time_str = list_to_int(time_str)


	#5 for test, 75 for 3 pages
	for submission in reddit.subreddit(subred).hot(limit=75):
		if (not submission.stickied):
			#add subreddit
			subred_name.append(subred)
			#add number online
			users_online.append(time_str)
			#add title to array
			#post_title.append(submission.title)
			#add time since posted
			post_made.append(get_time_since_posted(submission))
			#add net votes 
			net_votes.append(submission.score)
			#add percent upvotes
			up_ratio.append(submission.upvote_ratio)


df = pd.DataFrame(scraped_data)
df.to_csv(r'scraped_data.txt', header=None, index=None, sep=' ', mode='a')

print "Data saved to file scraped_data.txt in the format:"
print "\n"
print df.head()




