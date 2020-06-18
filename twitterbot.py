import requests

def twitter_bot():
	XBTUSD_json = get_XBTUSD_liquidations()
	ETHUSD_json = get_ETHUSD_liqudations()

	for liquidation in XBTUSD_json:
		orderID = get_orderID(liquidation)
		symbol = get_symbol(liquidation)
		side = get_side(liquidation)
		price = get_price(liquidation)
		quantity = get_quantity(liquidation)

		print(orderID, symbol, side, price, quantity)

	for liquidation in ETHUSD_json:
		orderID = get_orderID(liquidation)
		symbol = get_symbol(liquidation)
		side = get_side(liquidation)
		price = get_price(liquidation)
		quantity = get_quantity(liquidation)

		print(orderID, symbol, side, price, quantity)




def get_XBTUSD_liquidations():
	request = requests.get('https://www.bitmex.com/api/v1/liquidation?symbol=XBTUSD&count=50&reverse=true')
	print("BTC status", request.status_code)
	return request.json()

def get_ETHUSD_liqudations():
	request = requests.get('https://www.bitmex.com/api/v1/liquidation?symbol=ETHUSD&count=50&reverse=true')
	print("ETH status", request.status_code)
	return request.json()

def get_orderID(liquidation):
	return liquidation["orderID"]

def get_symbol(liquidation):
	return liquidation["symbol"]

def get_side(liquidation):
	return liquidation["side"]

def get_price(liquidation):
	return liquidation["price"]

def get_quantity(liquidation):
	return liquidation["leavesQty"]

twitter_bot()



