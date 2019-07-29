# deeID Websocket Server


# Data Structures

### Fiat-Shamir Identification
The QR Code on the client will run such a JSON:
'''
    'type': 'almasFFSRegister',
    'wsURL': 'https://lucror.serveo.net/',
    'uID': dataJSON['uID'],
    'expirytime' : '',
'''

### loginSigSigned

'''
    'type': 'loginSigSigned',
    'uID': ...
    'deeID': ...
    'expirytime': ...
    'data': ...
    'msg': ...
    'signature': ...
'''