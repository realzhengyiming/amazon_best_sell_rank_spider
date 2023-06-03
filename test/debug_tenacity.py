import tenacity


@tenacity.retry(
    stop=tenacity.stop_after_attempt(3),
    wait=tenacity.wait_fixed(0.5),
)
def get_data():
    # 这里是获取数据的代码
    # 如果发生异常，则会自动进行重试
    return 1 / 0


if __name__ == '__main__':
    print(get_data())
