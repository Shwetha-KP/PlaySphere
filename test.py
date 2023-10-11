from twilio.rest import Client
account_sid = 'ACc2247aac5dd488e8b68a9f991610d749'
auth_token = '46a4f987884ee15f62d5e7fba59fe0fb'
client = Client(account_sid, auth_token)
message = client.messages.create(
    body="hi",
    from_='+16562230942',
    to='+919740936895'
)
print(f"Message sent with SID: {message.sid}")
