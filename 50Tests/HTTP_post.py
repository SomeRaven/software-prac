import requests
import datetime
import csv
import random
import time

# Lambda function URL
url = 'https://4nzb5ltfm4a4l5a4omnvv23baq0ilpyz.lambda-url.us-west-1.on.aws/'

timestamp = str(datetime.datetime.now())

def read_csv(file_name):
    data = []
    with open(file_name, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data

def create_random_item(bank_data, merchant_data):
    bank_row = random.choice(bank_data)
    merchant_row = random.choice(merchant_data)

    item = {
        "BankName_CC": str(bank_row["BankName"]),
        "BankName_Merch": str(merchant_row["BankName"]),
        "merchant_name": str(merchant_row["MerchantName"]),
        "AccountNum_forCC": str(bank_row["AccountNum"]),
        "AccountNum_for_merch": str(merchant_row["AccountNum"]),
        "card_type": str(bank_row["CardType"]),
        "merchant_token": str(merchant_row["Token"]),
        "amount": str("{:.2f}".format(random.uniform(10.0, 100.0)))
    }
    return item

def post_request(item):
    result = requests.post(url, json=item)
    return result

def write_to_log(log_file, message):
    with open(log_file, 'a') as log:
        log.write(message + '\n')

def main():
    log_file = 'merchantSim.log'
    write_to_log(log_file, 'Simulation started at: ' + timestamp)

    bank_data = read_csv('bank_data.csv')
    merchant_data = read_csv('merchant_data.csv')
    items = []
    count1 = 1
    count2 = 1

    for i in range(50):
        random_item = create_random_item(bank_data, merchant_data)
        items.append(random_item)

    retry_attempts = 3  # Number of retry attempts
    for item in items:
        retries = 0
        while retries < retry_attempts:
            result = post_request(item)
            if result.text == "bank failure":  # If bank failure occurs
                retries += 1
                log_message = 'Bank failure for item: {} - Retrying...'.format(count1)
                print(log_message)
                write_to_log(log_file, log_message)
                time.sleep(1)  # Wait for a second before retrying
            else:
                success_message = 'Item {}: {}'.format(count1, result.text)
                print(success_message)
                write_to_log(log_file, success_message)
                count1 += 1
                break
        if retries == retry_attempts:
            max_retries_message = 'Max retries reached for item: {}'.format(item)
            print(max_retries_message)
            write_to_log(log_file, max_retries_message)
        else:
            count2 += 1

    write_to_log(log_file, 'Simulation ended.')

if __name__ == "__main__":
    main()
