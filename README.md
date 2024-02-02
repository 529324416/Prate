# Prate

prate is a single file python script which provide an api for you can show up a messagebox, this function usually used in local server.
when you build up a local server, and you want to show some tips, you can use prate to do this.

## usage

```python
from prate import Prate

msgbox = Prate()
msgbox.ring("title", "content")
```
this function can be used as a single component, but it can embedded into an application's loop

### used in flask application
```python

from flask import Flask
from prate import Prate

msgbox = Prate()

app = Flask(__name__)

@app.route("/ring")
def ring():
    msgbox.ring("Hello", "World")
    return ""
```
