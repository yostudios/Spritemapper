from os import path
from werkzeug.wsgi import SharedDataMiddleware
from werkzeug.wrappers import Request
from werkzeug.serving import run_simple
from werkzeug.utils import redirect
from werkzeug.exceptions import NotFound

@Request.application
def index_redirect(request):
    if request.path.endswith("/"):
        return redirect(request.url + "index.html")
    else:
        raise NotFound(request.url)
app = SharedDataMiddleware(redirect("/index.html"), {"/": path.dirname(__file__)})

def main():
    run_simple("127.0.0.1", 8000, app)

if __name__ == "__main__":
    main()
