# 自定义的异常类
class SeleniumGetPageError(Exception):
    """selenium 打开网页 检测到被反爬的情况"""

    def __init__(self):
        pass

    def __str__(self):
        return f"{self.__class__.__name__}: selenium打开网页失败，检测到被反爬，重新加入队列，等待下次请求"
