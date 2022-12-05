import requests
from datetime import datetime, timedelta
import os
from twilio.rest import Client

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
stock_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "outputsize": "compact",
    "apikey": STOCK_API_KEY,
}

news_params = {
    "q": COMPANY_NAME,
    "apiKey": NEWS_API_KEY,
}

date_yesterday = datetime.today().date() - timedelta(days=1)
date_yesterday_string = str(date_yesterday)
date_before_yesterday = str(date_yesterday - timedelta(days=1))
date_before_yesterday_string = str(date_before_yesterday)


## STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").

stock_response = requests.get(url=f'https://www.alphavantage.co/query', params=stock_params)
stock_response.raise_for_status()
stock_data = stock_response.json()

daily_close_data = {key: value["4. close"] for key, value in stock_data["Time Series (Daily)"].items()}
print(daily_close_data)

while date_yesterday_string not in daily_close_data or date_before_yesterday_string not in daily_close_data:
    if date_yesterday_string not in daily_close_data:
        date_yesterday -= timedelta(days=1)
        date_yesterday_string = str(date_yesterday)
        date_before_yesterday = date_yesterday - timedelta(days=1)
        date_before_yesterday_string = str(date_before_yesterday)
        continue
    date_before_yesterday = date_yesterday - timedelta(days=1)
    date_before_yesterday_string = str(date_before_yesterday)

def stock_price_diff(y, dby):
    percentage_diff = (float(y) - float(dby))/float(dby) * 100
    print(percentage_diff)
    if percentage_diff >= 0 or percentage_diff <= 0:
        return int(percentage_diff)

if stock_price_diff(daily_close_data[date_yesterday_string], daily_close_data[date_before_yesterday_string]):
    print("Get News")

## STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME. 

news_response = requests.get(url=f"https://newsapi.org/v2/everything", params=news_params)
news_data = news_response.json()
latest_news = [{"title": news["title"],
                "description": news["description"]} for news in news_data["articles"][0:3]]
print(latest_news)

## STEP 3: Use https://www.twilio.com
# Send a separate message with the percentage change and each article's title and description to your phone number.


client = Client(account_sid, auth_token)
#stock_price_diff(daily_close_data[date_yesterday_string], daily_close_data[date_before_yesterday_string])
if True:
    percentage_change = stock_price_diff(daily_close_data[date_yesterday_string], daily_close_data[date_before_yesterday_string])
    if percentage_change > 0:
        change = f"🔺{percentage_change}%"
    else:
        change = f"🔻{percentage_change}%"
    for news in latest_news:
        headline = news["title"]
        brief = news["description"]
        message = client.messages \
                    .create(
                         body=f"{STOCK}: {change}\nHeadline: {headline}\nBrief: {brief}",
                         from_='+19403705556',
                         to='+6585862167'
                     )
        print(message.sid)
#Optional: Format the SMS message like this: 
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""

