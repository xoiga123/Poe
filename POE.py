import requests
import time

url = 'https://www.quora.com/poe_api/gql_POST'

headers = {
    'Host': 'www.quora.com',
    'Accept': '*/*',
    'apollographql-client-version': '1.1.6-65',
    'Accept-Language': 'en-US,en;q=0.9',
    'User-Agent': 'Poe 1.1.6 rv:65 env:prod (iPhone14,2; iOS 16.2; en_US)',
    'apollographql-client-name': 'com.quora.app.Experts-apollo-ios',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
}

proxies = None

def set_proxy(proxy):
    proxy = {'https': proxy}

def set_auth(key, value):
    headers[key] = value

def load_chat_id_map(bot="a2", formkey=None, cookie=None, proxies=None):
    data = {
        'operationName': 'ChatViewQuery',
        'query': 'query ChatViewQuery($bot: String!) {\n  chatOfBot(bot: $bot) {\n    __typename\n    ...ChatFragment\n  }\n}\nfragment ChatFragment on Chat {\n  __typename\n  id\n  chatId\n  defaultBotNickname\n  shouldShowDisclaimer\n}',
        'variables': {
            'bot': bot
        }
    }
    if formkey:
        headers['Quora-Formkey'] = formkey
    if cookie:
        headers['Cookie'] = cookie
    response = requests.post(url, headers=headers, json=data, proxies=proxies)
    return response.json()['data']['chatOfBot']['chatId']

def send_message(message,bot="a2",chat_id="", formkey=None, cookie=None, proxies=None):
    data = {
    "operationName": "AddHumanMessageMutation",
    "query": "mutation AddHumanMessageMutation($chatId: BigInt!, $bot: String!, $query: String!, $source: MessageSource, $withChatBreak: Boolean! = false) {\n  messageCreate(\n    chatId: $chatId\n    bot: $bot\n    query: $query\n    source: $source\n    withChatBreak: $withChatBreak\n  ) {\n    __typename\n    message {\n      __typename\n      ...MessageFragment\n      chat {\n        __typename\n        id\n        shouldShowDisclaimer\n      }\n    }\n    chatBreak {\n      __typename\n      ...MessageFragment\n    }\n  }\n}\nfragment MessageFragment on Message {\n  id\n  __typename\n  messageId\n  text\n  linkifiedText\n  authorNickname\n  state\n  vote\n  voteReason\n  creationTime\n  suggestedReplies\n}",
    "variables": {
        "bot": bot,
        "chatId": chat_id,
        "query": message,
        "source": None,
        "withChatBreak": False
    }
}
    if formkey:
        headers['Quora-Formkey'] = formkey
    if cookie:
        headers['Cookie'] = cookie
    _ = requests.post(url, headers=headers, json=data, proxies=proxies)

def clear_context(chatid, formkey=None, cookie=None, proxies=None):
    data = {
        "operationName": "AddMessageBreakMutation",
        "query": "mutation AddMessageBreakMutation($chatId: BigInt!) {\n  messageBreakCreate(chatId: $chatId) {\n    __typename\n    message {\n      __typename\n      ...MessageFragment\n    }\n  }\n}\nfragment MessageFragment on Message {\n  id\n  __typename\n  messageId\n  text\n  linkifiedText\n  authorNickname\n  state\n  vote\n  voteReason\n  creationTime\n  suggestedReplies\n}",
        "variables": {
            "chatId": chatid
        }
    }
    if formkey:
        headers['Quora-Formkey'] = formkey
    if cookie:
        headers['Cookie'] = cookie
    _ = requests.post(url, headers=headers, json=data, proxies=proxies)

def get_latest_message(bot, retry=5, formkey=None, cookie=None, proxies=None):
    data = {
        "operationName": "ChatPaginationQuery",
        "query": "query ChatPaginationQuery($bot: String!, $before: String, $last: Int! = 10) {\n  chatOfBot(bot: $bot) {\n    id\n    __typename\n    messagesConnection(before: $before, last: $last) {\n      __typename\n      pageInfo {\n        __typename\n        hasPreviousPage\n      }\n      edges {\n        __typename\n        node {\n          __typename\n          ...MessageFragment\n        }\n      }\n    }\n  }\n}\nfragment MessageFragment on Message {\n  id\n  __typename\n  messageId\n  text\n  linkifiedText\n  authorNickname\n  state\n  vote\n  voteReason\n  creationTime\n}",
        "variables": {
            "before": None,
            "bot": bot,
            "last": 1
        }
    }
    if formkey:
        headers['Quora-Formkey'] = formkey
    if cookie:
        headers['Cookie'] = cookie
    author_nickname = ""
    state = "incomplete"
    for _ in range(retry):
        time.sleep(2)
        response = requests.post(url, headers=headers, json=data, proxies=proxies)
        response_json = response.json()
        text = response_json['data']['chatOfBot']['messagesConnection']['edges'][-1]['node']['text']
        state = response_json['data']['chatOfBot']['messagesConnection']['edges'][-1]['node']['state']
        author_nickname = response_json['data']['chatOfBot']['messagesConnection']['edges'][-1]['node']['authorNickname']
        if author_nickname==bot and state=='complete':
            return text
    return None

