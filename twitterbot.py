import requests
import tweepy
import os
import time
import schedule
from datetime import datetime, timezone

class FundingBot:
	def __init__(self, tickers_lst):
		self.dict = {ticker: get_funding(ticker) for ticker in tickers_lst}
		self.api = self.login()

	def __repr__(self):
		return "This bot is currently tracking: '" + "', '".join(sorted(ticker for ticker in self.dict.keys())) + "'."

	def login(self):
		access_token = os.environ['TWITTER_ACC_TOKEN'] 
		access_token_secret = os.environ['TWITTER_ACC_TOKEN_SECRET']
		api_key = os.environ['TWITTER_API_KEY']
		api_key_secret = os.environ['TWITTER_API_KEY_SECRET']

		auth = tweepy.OAuthHandler(api_key, api_key_secret)
		auth.set_access_token(access_token, access_token_secret)

		return tweepy.API(auth)

	def run(self): # Times in CEST, needs to be updated.
		self.schedule_funding_updates()
		self.schedule_tweets()
		while True:
			schedule.run_pending()
			time.sleep(60) # wait one minute
			print("Running")

	def update_funding(self):
		for ticker in self.dict.keys():
			self.dict[ticker] = get_funding(ticker)

	def schedule_funding_updates(self):
		schedule.every().day.at("06:01").do(self.update_funding)
		schedule.every().day.at("14:01").do(self.update_funding)
		schedule.every().day.at("22:01").do(self.update_funding)


	def schedule_tweets(self):
		for ticker in self.dict.keys():
			schedule.every().day.at("06:02").do(self.send_tweet, ticker)
			schedule.every().day.at("14:02").do(self.send_tweet, ticker)
			schedule.every().day.at("22:02").do(self.send_tweet, ticker)

	def add_ticker(self, ticker):
		if ticker not in self.dict:
			try:
				self.dict[ticker] = get_funding(ticker)
			except:
				print("Ticker '%s' is not a valid ticker." % ticker)
		else:
			print("Ticker: %s is already being tracked." % ticker)

	def remove_ticker(self, ticker):
		self.dict.pop(ticker, None)

	def send_tweet(self, ticker): # TODOO: Add timestamp for tweets not to be duplicates
		last_funding = self.dict[ticker]
		last_funding_rate = get_funding_rate(last_funding)

		second_last_funding = get_funding(ticker, False)
		second_funding_rate = get_funding_rate(second_last_funding)

		last_funding_rate_percentage = last_funding_rate*100
		percentage_change = round(calc_percentage_change(last_funding_rate, second_funding_rate), 2)

		if percentage_change >= 0:
		 	message = "📈 BitMEX Funding rate for $%s is now %s%%, an increase of %s%%" %(ticker, last_funding_rate_percentage, percentage_change)
		else:
			message = "📉 BitMEX Funding rate for $%s is now %s%%, a decrease of %s%%" %(ticker, last_funding_rate_percentage, percentage_change)
		
		self.api.update_status(message)

def get_funding(ticker, latest=True):
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
	return funding["timestamp"]

def get_symbol(funding):
	return funding["symbol"]

def get_funding_interval(funding):
	return funding["fundingInterval"]

def get_funding_rate(funding):
	return funding["fundingRate"]

def get_daily_funding_rate(funding):
	return funding["fundingRateDaily"]

def calc_percentage_change(newest, oldest):
	return ((newest - oldest)/abs(oldest))*100

if __name__ == "__main__":
	bot = FundingBot(["XBTUSD", "ETHUSD", "XRPUSD"])
	bot.run()
