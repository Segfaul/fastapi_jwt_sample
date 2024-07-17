import re

proxy_pattern = re.compile(
    r'^http:\/\/'  # starts with 'http://'
    r'(?P<login>[^:]+)'  # login part
    r':'  # colon separator
    r'(?P<password>[^@]+)'  # password part
    r'@'  # at symbol
    r'(?P<ip>[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)'  # IP address part
    r':'  # colon separator
    r'(?P<port>[0-9]+)$'  # port part
)


def validate_proxy(link: str) -> bool:
    '''
    Validate provided http proxy link
    '''
    return re.match(proxy_pattern, link) is not None
