import requests

class twitter_bot:
	def __init__(self, tickers_lst):
		self.dict = {ticker: request_latest_funding(ticker) for ticker in tickers_lst}

	def __repr__(self):
		return "This bot is currently tracking: '" + "', '".join(sorted(ticker for ticker in self.dict.keys())) + "'."

	def update_funding(self):
		for ticker in self.dict.keys():
			self.dict[ticker] = request_latest_funding(ticker)

	def add_ticker(self, ticker):
		if ticker not in self.dict:
			try:
				self.dict[ticker] = request_latest_funding(ticker)
			except:
				print("Ticker '%s' is not a valid ticker." % ticker)
		else:
			print("Ticker: %s is already being tracked." % ticker)

	def remove_ticker(self, ticker):
		self.dict.pop(ticker, None)

	def send_tweet(self, ticker):
		funding = self.dict[ticker]
		timestamp = get_timestamp(funding)
		symbol = get_symbol(funding)
		funding_interval = get_funding_interval(funding)
		funding_rate = get_funding_rate(funding)
		funding_rate_daily = get_daily_funding_rate(funding)

def request_latest_funding(ticker):
	request = requests.get("https://www.bitmex.com/api/v1/funding?symbol=%s&count=1&reverse=true" % ticker)
	json = request.json()
	if request.status_code == 200 and json:
		funding = json[0]
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


if __name__ == "__main__":
	bot = twitter_bot(["XBTUSD", "ETHUSD", "XRPUSD"])
	bot.add_ticker("XYZUSD")
