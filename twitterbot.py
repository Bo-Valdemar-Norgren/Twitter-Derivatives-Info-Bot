import requests
import tweepy
import os

class twitter_bot:
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

	def update_funding(self):
		for ticker in self.dict.keys():
			self.dict[ticker] = get_funding(ticker)

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

	def send_tweet(self, ticker):
		last_funding = self.dict[ticker]
		last_funding_rate = get_funding_rate(last_funding)

		second_last_funding = get_funding(ticker, False)
		second_funding_rate = get_funding_rate(second_last_funding)

		percentage_change = calc_percentage_change(second_funding_rate, last_funding_rate)

		# if percentage_change >= 0:
		# 	message = "BitMEX Funding rate for %s is now %s, an increase of %s%" (ticker, last_funding_rate, percentage_change)
		# else:
		# 	message = "BitMEX Funding rate for %s is now %s, a decrease of %s%" (ticker, last_funding_rate, percentage_change)
		
		#self.api.update_status("Testing")


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

def calc_percentage_change(first_num, second_num):
	return ((first_num - second_num)/abs(second_num))*100



if __name__ == "__main__":
	bot = twitter_bot(["XBTUSD", "ETHUSD", "XRPUSD"])
	bot.send_tweet("XBTUSD")
