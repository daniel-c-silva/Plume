import os
import webview

# * set to False after you've run `npm run build`
DEV = True

HERE = os.path.dirname(os.path.abspath(__file__))

if DEV:
    URL = "http://localhost:5173"  # the vite dev server
else:
    URL = os.path.join(HERE, "frontend", "Plume", "dist", "index.html")

STORAGE = os.path.join(HERE, ".plume-data")  # keeps localStorage between runs

webview.create_window("Plume", URL, width=420, height=760, min_size=(360, 600))
webview.start(private_mode=False, storage_path=STORAGE, http_server=True)   