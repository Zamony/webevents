import webbrowser
import webevents

def pong_callback(number):
    print(number)
    snakes_events.fire_event("ping", int(number) + 1)

address = ("localhost", 8080)
snakes_events = webevents.run(address, "web")
snakes_events.add_termination_callback(lambda: print("The end..."))
snakes_events.add_event_listener("pong", pong_callback)

webbrowser.open_new_tab("http://{}:{}".format(*address))

# initial ping
snakes_events.fire_event("ping", 0)

try:
    while True:
        pass
except KeyboardInterrupt:
    snakes_events.terminate()