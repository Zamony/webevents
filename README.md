# Webevents
A little, zero-dependency Python library for making simple HTML/JS GUI apps
## Installation
Note that only Python >= 3.6 is supported
```
pip install webevents
```
## Example: ping-pong
Python sends a number to Javascript, which outputs it out to console, increments it and sends the number back to Python for displaying in terminal. And so on.

We will have the directory structure presented below. Generally speaking, In the "web" folder you can put your HTML/CSS/JS application. "Ping-pong" application will only consist of one "index.html" file.

```
├── example.py
└── web
    └── index.html
```
**index.html:**
```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <title>Webevents "Ping-pong"</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <script src="webevents.js"></script>
</head>
<body>
  Demonstration in console
  <script>
  webevents.addEventListener("ping", function(number){
    console.log(number);
    webevents.fireEvent("pong", number+1);
  });
  </script>
</body>
</html>
```

**example.py:**
```python
import webbrowser
import webevents

def pong_callback(number):
    print(number)
    snakes_events.fire_event("ping", int(number) + 1)

address = ("localhost", 8080)
snakes_events = webevents.run(address, "web")
snakes_events.add_termination_callback(lambda: print("The end!"))
snakes_events.add_event_listener("pong", pong_callback)

webbrowser.open_new_tab("http://{}:{}".format(*address))

# initial ping
snakes_events.fire_event("ping", 0)

try:
    while True:
        pass
except KeyboardInterrupt:
    snakes_events.terminate()
```

Multiple callbacks are supported. You can remove events with:
+ `remove_event_listener(event_type, callback)` in Python
+ `removeEventListener(event_type, callback)` in JS

In Python you can add termination callbacks with `add_termination_callback(callback)`. It may be useful in multi process applications. Note that there is no need to add termination callbacks if you don't need them.

Usually termination is occurred when user closes the browser page. But you can disable this by passing `timeout=None` in `webevents.run()`. You always can terminate the "webevents" with `webevents.terminate()`.

**Javascript output:**
```
0 2 4 6 8 10 12 ...
```
**Python output:**
```
1 3 5 7 9 11 13 ... The end!
```