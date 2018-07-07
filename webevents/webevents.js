var webevents = (function () {
  var subscribers = {};

  function addEventListener(type, fn) {
    if (!subscribers[type]) {
      subscribers[type] = [];
    }
    if (subscribers[type].indexOf(fn) == -1) {
      subscribers[type].push(fn);
    }
  }

  function removeEventListener(type, fn) {
    var listeners = subscribers[type];

    if (!listeners) return;

    var index = listeners.indexOf(fn);

    if (index > -1) {
      listeners.splice(index, 1);
    }
  }

  function _publishEvent(type, e) {
    if (!subscribers[type]) return;

    var listeners = subscribers[type];

    for (var i = 0, length = listeners.length; i < length; i++) {

      listeners[i](e);
    }
  }

  function fireEvent(type, data) {
    let form_data = new FormData()
    form_data.append("data", JSON.stringify(data));
    form_data.append("event_type", type);
    fetch("/snakes_send", {
      method: 'POST',
      body: form_data
    }).catch(error => console.error('Error:', error))    
  }

  function _pullEvent() {
    fetch("/snakes_receive.json")
      .then((resp) => resp.json())
      .then(function (event) {
        if (event != ""){
          _publishEvent(event.event_type, event.data);
        }
      })
      .catch(function (error) {
        console.log(error);
      });
    setTimeout(_pullEvent, 1000);
  }

  function getFormSerialization(form_element){
    data = {}
    var arr = Array.from(new URLSearchParams(new FormData(form_element)).entries());
    arr.forEach(function (subarr) {
      data[subarr[0]] = subarr[1];
    });
    return data;
  }

  return {
    fireEvent: fireEvent,
    addEventListener: addEventListener,
    removeEventListener: removeEventListener,
    getFormSerialization: getFormSerialization,
    _publishEvent: _publishEvent,
    _pullEvent: _pullEvent
  };
})();

setTimeout(webevents._pullEvent, 1000);
