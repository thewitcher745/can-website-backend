import os

from app_prepare import app
from routes import *

from v2.posts import PublicPostsRouter, AdminPostsRouter
from v2.auth import AuthManager

PublicPostsRouter.register_routes()
AdminPostsRouter.register_routes()
AuthManager.register_routes()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
