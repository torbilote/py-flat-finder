from app.utils import Finder
from app.config import web_url

def run() -> None:
    '''Main function.'''
    finder = Finder(web_url)
    finder.send_http_request()
    print(finder.response)
if __name__ == '__main__':
    run()
