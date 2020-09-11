url_to_session = 'https://vk.com/'
url_to_friends = 'https://vk.com/al_friends.php'

headers_to_session = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
        (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language':'ru-ru,ru;q=0.8,en-us;q=0.5,en;q=0.3',
        'Accept-Encoding':'gzip, deflate',
        'Connection':'keep-alive',
        'DNT':'1'
    }

data_to_friends = {
        'act': 'load_friends_silent',
        'id': '{}',
        'al': '1',
        'gid': '0',
    }
