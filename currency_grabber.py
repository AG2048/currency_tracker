import requests

def get_currency_rate(currency_name_chinese, url, index=2):
    # It's a website in chinese, so encoding
    try:
        response = requests.get(url)
    except:
        print("Failed to connect to the website")
        return "Failed to connect to the website"
    content = response.content.decode("utf-8")
    # print(content)
    try:
        splitted = content.split("<td>"+currency_name_chinese+"</td>")[1]
    except:
        print("Failed to find the currency name")
        return "Failed to find the currency name"
    numbers = splitted.split("<td>")[1:5]
    rates = []
    for number in numbers:
        number = number.replace("</td>", "").strip()
        rates.append(float(number))
    return rates[index]