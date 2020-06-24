import requests
import tweepy
import os
import time
import arrow
import schedule
import datetime
from dateutil.parser import parse

class FundingBot:
	def __init__(self, tickers_lst):
		self.current_funding_dict = {ticker: get_funding(ticker, latest=True) for ticker in tickers_lst}
		self.api = self.login()

	def __repr__(self):
		return "This bot is currently tracking: '" + "', '".join(sorted(ticker for ticker in self.dict.keys())) + "'."

	def login(self):
		"""
		Uses twitter keys to gain account access.
		"""
		access_token = os.environ['TWITTER_ACC_TOKEN'] 
		access_token_secret = os.environ['TWITTER_ACC_TOKEN_SECRET']
		api_key = os.environ['TWITTER_API_KEY']
		api_key_secret = os.environ['TWITTER_API_KEY_SECRET']

		auth = tweepy.OAuthHandler(api_key, api_key_secret)
		auth.set_access_token(access_token, access_token_secret)

		return tweepy.API(auth)

	def run(self):
		"""
		Starts the bot.
		"""
		self.schedule_funding_updates()
		self.schedule_tweets()
		while True:
			schedule.run_pending()
			time.sleep(60) # Checks for pending jobs every minute.

	def update_funding(self):
		"""
		Updates the current_funding_dict. 
		"""
		for ticker in self.current_funding_dict.keys():
			self.current_funding_dict[ticker] = get_funding(ticker, latest=True)

	def schedule_funding_updates(self):
		"""
		Schedules the bot to retreive updated fundings at certain times.

		Bitmex updates funding for contracts at 04:00, 12:00, 20:00 UTC. 
		Funding is retreived a minute after the update to ensure up to date fundings.
		"""
		first_funding_update = military_utc_to_local(4, 1)
		second_funding_update = military_utc_to_local(12, 1)
		third_funding_update = military_utc_to_local(20, 1)

		schedule.every().day.at(first_funding_update).do(self.update_funding)
		schedule.every().day.at(second_funding_update).do(self.update_funding)
		schedule.every().day.at(third_funding_update).do(self.update_funding)


	def schedule_tweets(self):
		"""
		Schedules the bot to send tweets at certain times.

		Bitmex updates funding for contracts at 04:00, 12:00, 20:00 UTC. 
		Tweets are sent two minutes after the funding update to ensure up to date fundings.
		"""
		first_funding_update = military_utc_to_local(4, 2)
		second_funding_update = military_utc_to_local(12, 2)
		third_funding_update = military_utc_to_local(20, 2)

		for ticker in self.current_funding_dict.keys():
			schedule.every().day.at(first_funding_update).do(self.send_tweet, ticker)
			schedule.every().day.at(second_funding_update).do(self.send_tweet, ticker)
			schedule.every().day.at(third_funding_update).do(self.send_tweet, ticker)

	def add_ticker(self, ticker):
		"""
		Adds a ticker to be tracked by the bot.
		"""
		if ticker not in self.current_funding_dict:
			try:
				self.dict[ticker] = get_funding(ticker, latest=True)
			except:
				print("Ticker '%s' is not a valid ticker." % ticker)
		else:
			print("Ticker: %s is already being tracked." % ticker)

	def remove_ticker(self, ticker):
		"""
		Removes a ticker from being tracked.
		"""
		self.current_funding_dict.pop(ticker, None)

	def send_tweet(self, ticker):
		"""
		Sends a tweet about the funding status of the ticker.
		"""
		last_funding = self.current_funding_dict[ticker]
		last_funding_rate = get_funding_rate(last_funding)
		last_funding_timestamp = get_timestamp(last_funding)

		parsed_timestamp = parse(last_funding_timestamp).strftime("%b %d %Y %H:%M")

		penultimate_funding = get_funding(ticker, latest=False)
		penultimate_funding_rate = get_funding_rate(penultimate_funding)

		last_funding_rate_percentage = last_funding_rate*100
		percentage_change = round(calc_percentage_change(last_funding_rate, penultimate_funding_rate), 2)

		if percentage_change >= 0:
		 	message = """
		 	%s
		 	📈 BitMEX Funding rate for $%s is now %s%%, an increase of %s%%""" %(parsed_timestamp, ticker, last_funding_rate_percentage, percentage_change)
		else:
			message = """
			%s
			📉 BitMEX Funding rate for $%s is now %s%%, a decrease of %s%%""" %(parsed_timestamp, ticker, last_funding_rate_percentage, percentage_change)
		
		self.api.update_status(message)

def get_funding(ticker, latest):
	"""
	Returns the latest funding or the penultimate funding depending on the latest boolean.
	"""
	request = requests.get("https://www.bitmex.com/api/v1/funding?symbol=%s&count=2&reverse=true" % ticker)
	json = request.json()
	if request.status_code == 200 and json:
		if latest:
			funding = json[0]
			return funding
		else:
			funding = json[1]
			return funding
	else:
		e = Exception("Latest funding for the ticker %s could not be retrieved." % ticker)
		print(e)
		raise e

def get_timestamp(funding):
	"""
	Returns the timestamp from a funding object.
	"""
	return funding["timestamp"]

def get_symbol(funding):
	"""
	Returns the symbol from a funding object.
	"""
	return funding["symbol"]

def get_funding_interval(funding):
	"""
	Returns the funding interval from a funding object.
	"""
	return funding["fundingInterval"]

def get_funding_rate(funding):
	"""
	Returns the funding rate from a funding object.
	"""
	return funding["fundingRate"]

def get_daily_funding_rate(funding):
	"""
	Returns the daily funding rate from a funding object.
	"""
	return funding["fundingRateDaily"]

def calc_percentage_change(newest, oldest):
	"""
	Returns the percentage change of two numbers.
	"""
	return ((newest - oldest)/abs(oldest))*100

def military_utc_to_local(hour, minute):
	"""
	Converts military utc to military local time.
	"""
	utc = arrow.utcnow().replace(hour=hour, minute=minute)
	return utc.to('local').format('HH:mm')

if __name__ == "__main__":
	bot = FundingBot(["ETHUSD", "XBTUSD", "XRPUSD"])
	bot.send_tweet("XBTUSD")
	bot.run()
