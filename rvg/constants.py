import re

USER_AGENT_HEADER = {'User-Agent': 'Mozilla/5.0'}
REDDIT_HOST = 'v.redd.it'
REDDIT_URL_PATTERN = re.compile(r'(https://www\.reddit\.com/r/[\w/]+)')
HTTP_REQUESTS_TIMEOUT = 60
