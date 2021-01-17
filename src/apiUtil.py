import requests

### Run get request while handling errors
async def call_get_request(ctx, url, params={}, headers={}):
    r = None
    try:
        r = requests.get(url = url, params = params, headers=headers)
    except Exception as e:
        if 'Max retries exceeded with url' in str(e):
            await ctx.send('Hello anyone there? 👀 👀 👀 [Unable to contact backend]')
        else:
            print(e)
            await ctx.send('Unknown exception for API call request, check logs')
    return r
### Run post request while handling errors
async def call_post_request(ctx, url, data={}):
    r = None
    try:
        r = requests.post(url = url, json = data)
    except Exception as e:
        if 'Max retries exceeded with url' in str(e):
            await ctx.send('Hello anyone there? 👀 👀 👀 [Unable to contact backend]')
        else:
            print(e)
            await ctx.send('Unknown exception for API post request, check logs')
    return r
### Check and handle any non-200 responses
async def handle_api_response(ctx, r):
    if r is None:
        print('couldnt contact server')
    elif r.status_code == 200:
        return r
    elif r.status_code == 401:
        print('[401] Unauthorized request:', r)
        await ctx.send('[401] Unauthorized request 🔒')
    else:
        print(r)
        print('Other: response code:', r.status_code)
        await ctx.send('{}'.format(r.text))
    return None
