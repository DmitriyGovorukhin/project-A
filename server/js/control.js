window.onload = function () {
    var l = document.getElementById('log');
    var button = document.getElementById('btn');

    function log(text) {
        l.value += (text + '\n');
        l.scrollTop = l.scrollHeight;
    }

    var port1 = 8090;
    var port2 = 8091;

    var url1 = 'ws://' + document.location.hostname + ':' + port1 + '/';
    var url2 = 'ws://' + document.location.hostname + ':' + port2 + '/';

    var player;

    var connected = false;

    var socket;

    button.onclick = function () {
        if (!connected) {
            socket = new WebSocket(url1);

            socket.onopen = function () {
                log("connected to " + url1);

                socket.send(JSON.stringify({client: "browser", cmd: "video_start"}))
            };

            socket.onclose = function (event) {
                if (event.wasClean) {
                    log('close');
                } else {
                    log('disconnected');
                }

                log('code: ' + event.code + ' reason: ' + event.reason);

                button.innerHTML = "connect";

                connected = 0;
            };

            socket.onmessage = function (event) {
                // var obj = JSON.parse(event.data);
                log(event.data)
            };

            player = new JSMpeg.Player(url2, {canvas: document.getElementById('video-canvas')});

            button.innerHTML = "disconnect";

            connected = true;
        } else {
            player.pause();

            player = null;

            socket.close();

            socket = null;

            button.innerHTML = "connect";

            connected = false;
        }

        button.blur();
    };

    var x = document.getElementById('x');
    var y = document.getElementById('y');

    var state = {
        x: 0,
        y: 0
    };

    function axis(e) {
        var a = e.axis;
        var val = Math.round(e.value * 100) / 100;

        if (a === "RIGHT_STICK_X") {
            x.innerHTML = "X:" + val;

            state.x = val;
        }

        if (a === "RIGHT_STICK_Y") {
            y.innerHTML = "Y:" + val;

            state.y = val;
        }

        if (socket !== null && socket !== undefined) {
            socket.send(JSON.stringify(state))
        }
    }

    var gamepad = new Gamepad();

    gamepad.bind(Gamepad.Event.CONNECTED, function (device) {
        log("Connected " + device.id)
    });

    gamepad.bind(Gamepad.Event.DISCONNECTED, function (device) {
        log("Disconnected " + device.id)
    });

    gamepad.bind(Gamepad.Event.BUTTON_DOWN, function (e) {
        log("BUTTON_DOWN " + e.control)
    });

    gamepad.bind(Gamepad.Event.BUTTON_UP, function (e) {
        log("BUTTON_UP " + e.control)
    });

    gamepad.bind(Gamepad.Event.AXIS_CHANGED, function (e) {
        log("AXIS_CHANGED " + e.axis + " " + Math.round(e.value * 100) / 100);

        axis(e)
    });

    if (!gamepad.init()) {
        log('Your browser does not support gamepads, get the latest Google Chrome or Firefox')
    }
};

