from fastapi import FastAPI
from starlette.responses import HTMLResponse

app = FastAPI()


@app.get("/root", response_class=HTMLResponse)
async def home():
    """
    主页，包含一个指向目标页面的链接
    """
    return """
    <html>
        <head>
            <title>主页</title>
        </head>
        <body>
            <h1>欢迎访问主页</h1>
            <a href="/target/helloworld">点击这里跳转到目标页面</a>
        </body>
    </html>
    """


@app.get("/target/helloworld/{page_id}", response_class=HTMLResponse)
async def target(page_id):
    """
    目标页面
    """
    return f"""
    <html>
        <head>
            <title>目标页面</title>
        </head>
        <body>
            <h1>欢迎访问目标页面 {page_id}</h1>
        </body>
    </html>
    """

