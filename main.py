#!/usr/bin/env python
import asyncio, websockets
import datetime, uuid, sys
import random, string, json
from almasFFS import almasFFS

almasFFSSocket = {}
serverIP = '127.0.0.1'

# Port number to use
if (len(sys.argv) > 1):
    serverPort = sys.argv[1]
else:
    serverPort = 5678

print('Starting socket server....')
print('Running on http://'+str(serverIP)+':'+str(serverPort))

# Number of rounds for the Fiat-Shamir Protocol
almasFFSRounds = 5


# Signed login signature
async def loginSig(data):
    if almasFFSSocket[data['uID']]:
        sigJSON = json.dumps({
                    'type': 'loginSigSigned',
                    'uID': data['uID'],
                    'deeID': data['deeID'],
                    'expirytime': data['expirytime'],
                    'data': data['data'],
                    'msg': data['msg'],
                    'signature': data['signature']
                })
        await almasFFSSocket[data['uID']]['sock'].send(sigJSON)

# Structure of a common json
async def almasFFSSendJson(round, step, data, websocket):
    expJSON = json.dumps({'type' : 'almasFFS', 'round': round, 'rnds' : almasFFSRounds, 'step' : step, 'data' : data })
    await websocket.send(expJSON)

'''
async def almasFFSHandler(data, websocket):
    v = almasFFSSocket[id(websocket)]['v']
    n = almasFFSSocket[id(websocket)]['n']
    e = almasFFSSocket[id(websocket)]['e']
    x = almasFFSSocket[id(websocket)]['x']
    rnd = almasFFSSocket[id(websocket)]['rnd']

    if (data['step'] == 0):
        # Initial setup, to calculate the users 
        #   public key from the global function
        if(rnd < 1):
            I = str(data['data']['I'])
            j = data['data']['j']
            newN = int(data['data']['n'])
            almasFFSSocket[id(websocket)]['n'] = newN
            user = almasFFS(I, j, newN)
            almasFFSSocket[id(websocket)]['v'] = user.getPubKeys()
    
        almasFFSSocket[id(websocket)]['rnd'] += 1
        almasFFSSocket[id(websocket)]['x'] = 0
        almasFFSSocket[id(websocket)]['e'] = []

        await almasFFSSendJson(rnd+1, 1, '', websocket)

    elif (data['step'] == 1):
        # Get and save x
        almasFFSSocket[id(websocket)]['x'] = int(data['data'])
        # Send random bits
        for i in range(0,len(v)):
            e.append(random.randint(0,1))
        await almasFFSSendJson(rnd, 2, e, websocket)    
        almasFFSSocket[id(websocket)]['e'] = e

    elif (data['step'] == 3):
        # Step 3, get y
        expected_x = int(data['data'])**2 % n
        for i in range(0,len(e)):
            if e[i]==1:
                expected_x*=v[i]
        expected_x = expected_x % n

        # Step 4: Get the result
        if (expected_x==x) or (expected_x==(-x%n)):
            print("Challenge correctly completed!")
            await almasFFSSendJson(rnd, 4, 'Pass', websocket)    
        else:
            print("Failure in challenge")
            almasFFSSocket[id(websocket)]['fails'] += 1
            await almasFFSSendJson(rnd, 4, 'Fail', websocket)

        if(almasFFSSocket[id(websocket)]['rnd'] == almasFFSRounds):
            print('Fails: ' + str(almasFFSSocket[id(websocket)]['fails']))
'''

# Fiat-Shamir Cryptoo Mobile Handler
# Calls from the mobile phone will be led to here
#
# This function performs the Fiat-Shamir interactive
#  negotiation to prove ones identity.
async def almasFFSMobileHandler(data, websocket):
    socketID = int(data['forID'])
    v = almasFFSSocket[socketID]['v']
    n = almasFFSSocket[socketID]['n']
    e = almasFFSSocket[socketID]['e']
    x = almasFFSSocket[socketID]['x']
    rnd = almasFFSSocket[socketID]['rnd']
    # # ==================================
    # # STEP 0
    # # ==================================
    if (data['step'] == 0):
        # Initial setup, to calculate the users 
        #   public key from the global function
        if(rnd < 1):
            I = str(data['data']['I'])
            j = data['data']['j']
            j = list(map(int, j))
            newN = int(data['data']['n'])
            almasFFSSocket[socketID]['n'] = newN
            user = almasFFS(I, j, newN)
            almasFFSSocket[socketID]['v'] = user.getPubKeys()
    
        almasFFSSocket[socketID]['rnd'] += 1
        almasFFSSocket[socketID]['x'] = 0
        almasFFSSocket[socketID]['e'] = []

        print("the public key: " )
        print(almasFFSSocket[socketID]['v'])
        await almasFFSSendJson(rnd, 1, '', websocket)

    # # ==================================
    # # STEP 1 - GET x = s.r^2 mod n
    # # ==================================
    elif (data['step'] == 1):
        # Get and save x
        almasFFSSocket[socketID]['x'] = int(data['data'])
    # # ==================================
    # # STEP 2 - SEND RAND BITS
    # # ==================================
        # Send random bits
        e = []
        for i in range(0,len(v)):
            e.append(random.randint(0,1))    
        await almasFFSSendJson(rnd, 2, e, websocket)    
        almasFFSSocket[socketID]['e'] = e

    # # ==================================
    # # STEP 3 - GET Y 
    # # ==================================
    elif (data['step'] == 3):
        # Step 3, get y
        expected_x = int(data['data'])**2 % n

    # # ==================================
    # # STEP 4 - Verify y
    # # ==================================
        for i in range(0,len(e)):
            if e[i]==1:
                expected_x*=v[i]
        expected_x = expected_x % n

        print("expected x: "+str(expected_x))
    # # ==================================
    # # STEP final - GET THE RESULTS
    # # ==================================
        if (expected_x==x) or (expected_x==(-x%n)):
            print("Challenge correctly completed!")
            await almasFFSSendJson(rnd, 4, 'Pass', websocket)    
        else:
            print("Failure in challenge")
            almasFFSSocket[socketID]['fails'] += 1
            await almasFFSSendJson(rnd, 4, 'Fail', websocket)

        if(almasFFSSocket[socketID]['rnd'] == almasFFSRounds):
            fails = int(almasFFSSocket[socketID]['fails'])
            print('### Fails: ' + str(fails))
            finalResult = ''
            if (fails == 0):
                finalResult = 'Pass'
            elif (fails > 0):
                finalResult = 'Fail'
            else:
                finalResult = 'Error'

            await almasFFSSendJson(rnd, 4, finalResult, almasFFSSocket[socketID]['sock'])
            print('END OF AUTH')


async def main(websocket, path):
    uID = str(uuid.uuid4()) # a unique id for the connection
    #sockets[uID] = websocket
    almasFFSSocket[id(websocket)] = {
        'sock' : websocket,
        'uID' : uID,
        'v' : [],
        'n' : 0,
        'e' : [],
        'x' : 0,
        'rnd' : 0,
        'fails' : 0,
        'almasFFS' : 0,
    }

    socketID = id(websocket)

    uIDJson = json.dumps({'type': 'uID', 'uID': socketID})
    await websocket.send(uIDJson)
    

    try:
        async for message in websocket:
            #print('...New connection')

            data = json.loads(message)
            # if its a login attempt
            if(data['type'] == 'loginSig'):
                await loginSig(data)
            elif(data['type'] == 'almasFFS'):
                await almasFFSHandler(data, websocket)
            elif(data['type'] == 'almasFFSMobile'):
                await almasFFSMobileHandler(data, websocket)

    finally:
        #del sockets[uID]
        del almasFFSSocket[id(websocket)]


start_server = websockets.serve(main, serverIP, int(serverPort))

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
