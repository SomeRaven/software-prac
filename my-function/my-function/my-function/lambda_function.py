import json
import boto3
import datetime
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
merchant_table = dynamodb.Table('Merchant')
bank_table = dynamodb.Table('bank')
clearing_house_table = dynamodb.Table('clearingHouse')

status = 200
message = []

def echo_back(response,status):
    result = {
        "statusCode": status,
        "headers": {
            "Content-Type": "text/html"
        },
        "body": response
    }
    return result

def saveTransaction(transaction_id, merchant_name, bank_for_merch, bank_for_CC, AccountNum_for_CC, AccountNum_for_merch, amount, type_of_card):
    transaction_data = {
        'id': transaction_id,
        'MerchantName': merchant_name,
        'BankName_Merch': bank_for_merch,
        'BankName_CC': bank_for_CC,
        'AccountNum_forCC': AccountNum_for_CC[-4:],
        'AccountNum_for_merch': AccountNum_for_merch,
        'Amount': amount,
        'Type_of_Card': type_of_card,
        'status': status,
        'message': message
        }
    clearing_house_table.put_item(Item=transaction_data)

def merchant(transaction_id, merchant_name, bank_for_merch, bank_for_CC, AccountNum_for_CC, AccountNum_for_merch, amount, type_of_card, merchant_token):
    response_merchant = merchant_table.query(
            KeyConditionExpression=Key('MerchantName').eq(merchant_name)
        )

    if not response_merchant['Items']:
        status = 404
        message.append('Merchant bank not found')
        saveTransaction(transaction_id, merchant_name, bank_for_merch, bank_for_CC, AccountNum_for_CC, AccountNum_for_merch, amount, type_of_card)
        return echo_back(message, status)
    account_num_to_find = AccountNum_for_merch
    merchant_item = None
    print(response_merchant.get('merchant_item'),"!=", merchant_name)
    for item in response_merchant['Items']:
        if int(item.get('AccountNum')) == int(account_num_to_find):
            merchant_item = item
            break


    if merchant_item == None:
        status = 404
        message.append('Merchant bank not found')
        saveTransaction(transaction_id, merchant_name, bank_for_merch, bank_for_CC, AccountNum_for_CC, AccountNum_for_merch, amount, type_of_card)
        return echo_back(message, status)

    if int(merchant_item.get('AccountNum')) != int(AccountNum_for_merch):
        status = 404
        message.append('Invalid merchant account number')

    # Validating merchant token
    if merchant_item['Token'] != merchant_token:
        status = 404
        message.append('Merchant not authorized')

def bank(transaction_id, merchant_name, bank_for_merch, bank_for_CC, AccountNum_for_CC, AccountNum_for_merch, amount, type_of_card):
    # Querying Bank Table for Credit Card
    response_bank_CC = bank_table.query(
        KeyConditionExpression=Key('BankName').eq(bank_for_CC)
    )

    if not response_bank_CC['Items']:
        status = 404
        message.append('Bank for credit card not found')
    # Finding the bank item with the correct account number
    account_num_to_find = AccountNum_for_CC
    bank_item_CC = None
    for item in response_bank_CC['Items']:
        if int(item.get('AccountNum')) == int(account_num_to_find):
            bank_item_CC = item
            break

    if bank_item_CC is None:
        status = 404
        message.append('Bank item with the specified account number not found')
        saveTransaction(transaction_id, merchant_name, bank_for_merch, bank_for_CC, AccountNum_for_CC, AccountNum_for_merch, amount, type_of_card)
        return echo_back(message)


    # Validating Credit Card Account Number
    if int(bank_item_CC.get('AccountNum')) != int(AccountNum_for_CC):
        status = 404
        message.append('Invalid credit card account number')

    if type_of_card == 'Debit':
        if float(bank_item_CC['Balance']) < float(amount):
            status = 200
            message.append('Insufficient funds')
    else:
        if float(bank_item_CC['CreditUsed']) < float(amount) and float(bank_item_CC['CreditUsed']) + float(amount) > int(bank_item_CC['CreditLimit']):
            status = 200
            message.append('Insufficient funds')

def lambda_handler(event, context):
    print(event)
    if 'body' in event and event['body'] is not None:
        body = json.loads(event['body'])
        bank_for_merch = body.get('BankName_Merch')
        bank_for_CC = body.get('BankName_CC')
        merchant_name = body.get('merchant_name')
        AccountNum_for_CC = body.get('AccountNum_forCC')
        AccountNum_for_merch = body.get('AccountNum_for_merch')
        merchant_token = body.get('merchant_token')
        amount = body.get('amount')
        type_of_card = body.get('card_type')

        # Generate transaction ID using current date and time
        transaction_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")

        merchant(transaction_id, merchant_name, bank_for_merch, bank_for_CC, AccountNum_for_CC, AccountNum_for_merch, amount, type_of_card, merchant_token)

        bank(transaction_id, merchant_name, bank_for_merch, bank_for_CC, AccountNum_for_CC, AccountNum_for_merch, amount, type_of_card)

        # Transaction is valid, save to clearing house
        saveTransaction(transaction_id, merchant_name, bank_for_merch, bank_for_CC, AccountNum_for_CC, AccountNum_for_merch, amount, type_of_card)
        # All validations passed, proceed with the transaction
        return echo_back(message, status)
    else:
        return echo_back('Invalid request', 404)
    return echo_back(message, status)

