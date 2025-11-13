import requests
import json

url = 'https://sports-api.cloudbet.com/pub/v2/odds/competitions/soccer-england-premier-league/?markets=soccer.double_chance&players=false'
headers = {
    "accept": "application/json",
    "X-API-Key": "eyJhbGciOiJSUzI1NiIsImtpZCI6Img4LThRX1YwZnlUVHRPY2ZXUWFBNnV2bktjcnIyN1YzcURzQ2Z4bE44MGMiLCJ0eXAiOiJKV1QifQ.eyJhY2Nlc3NfdGllciI6ImFmZmlsaWF0ZSIsImV4cCI6MjA3ODMzNDc0NCwiaWF0IjoxNzYyOTc0NzQ0LCJqdGkiOiI1ZWIwNGZjNS0xMjhiLTRhNGEtOTMyNS03Nzk3M2IwYjFmOWQiLCJzdWIiOiIxN2U0ZDk4MS1jODA1LTRkZDMtYmVmYi01NzhjNTkwNWMwY2EiLCJ0ZW5hbnQiOiJjbG91ZGJldCIsInV1aWQiOiIxN2U0ZDk4MS1jODA1LTRkZDMtYmVmYi01NzhjNTkwNWMwY2EifQ.leilGTjGj7zcxFC9zmsUAsK0UAezmGw9aZZrdFHtqtmO821nm4jr7HmqBVgtKzUTPEGpj10JPZVAjf-yr-F83iVLHQrclei-V-q56gxww8GPDd2ns8TMtOfU7SmWgiRzAa7e3wbFwurN9OgmIX-wYo6WvvBPPEdHWi2JesIORGyC8JwIW4f3O8pCcnCOvts2cE9sjO_WoocX-rW9a11EtgfgYST_JvmcvcXoA-Wt7BB3wjOXHuleYY2jT1vwjvlNTQFKPcRdzls_z2EhkUE6BJmpqsfGdNfNje7pYp3zqBzW0Q_lFkZuUZ1j3s2d_RCShU5YzMBbvIJiB0ss4SwCtw"
}

response = requests.get(url, headers=headers)
print(response.status_code)
print(response.json())
with open("test5.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(response.json(), indent=4))
