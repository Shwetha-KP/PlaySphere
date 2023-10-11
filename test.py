from twilio.rest import Client
account_sid = 'ACc2247aac5dd488e8b68a9f991610d892'
auth_token = '46a4f987884ee15f62d5e7fba59fy178'
client = Client(account_sid, auth_token)
message = client.messages.create(
    body="hi",
    from_='+2389123098',
    to='+1234567890'
)
print(f"Message sent with SID: {message.sid}")
