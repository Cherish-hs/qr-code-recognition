
import webbrowser


def open_url(url):
    """使用系统默认浏览器打开网址。"""
    try:
        success = webbrowser.open(url)

        if success:
            print("已请求打开网址：", url)
        else:
            print("浏览器未能打开网址：", url)

        return success

    except Exception as e:
        print("打开网址失败：", e)
        return False
