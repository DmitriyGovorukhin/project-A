server = "http://" + window.location.hostname + ":8088/janus";

var janus = null;
var streamBigVideo = null;
var streamSmallVideo = null;

var started = false;

function log(msg) {
    var l = document.getElementById('log');

    var time = '[' + new Date().toUTCString() + '] ';

    var text = time + msg;
    l.value += text + '\n';
    l.scrollTop = l.scrollHeight;

    console.log(text)
}

function createVideoHandler(video, id) {
    var streaming;

    return {
        attach: {
            plugin: "janus.plugin.streaming",
            success: function (pluginHandle) {
                streaming = pluginHandle;

                log("Plugin attached! (" + streaming.getPlugin() + ", id=" + streaming.getId() + ")");
                // Setup streaming session
                updateStreamsList(id, streaming);
            },
            error: function (error) {
                log("  -- Error attaching plugin... " + error);

                console.error("Error attaching plugin... " + error);
            },
            onmessage: function (msg, jsep) {
                log(" ::: Got a message :::");

                log(JSON.stringify(msg));

                processMessage(msg);

                handleSDP(jsep, streaming);
            },
            onremotestream: function (stream) {
                log(" ::: Got a remote stream :::");

                log(JSON.stringify(stream));

                // Show the stream and hide the spinner when we get a playing event
                log("attaching remote media stream");

                Janus.attachMediaStream(video.get(0), stream);

                video.bind("playing", function () {
                    log("got playing event");
                });
            },
            oncleanup: function () {
                log(" ::: Got a cleanup notification :::");
            }
        },

        stop: function () {
            log("stopping stream");

            var body = {"request": "stop"};

            streaming.send({"message": body});

            streaming.hangup();
        }
    }
}

var portWs = 8091;

var wsPath = 'ws://' + document.location.hostname + ':' + portWs + '/';

var socket;

$(document).ready(function () {
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

    // Initialize the library (console debug enabled)
    Janus.init({
        debug: true, callback: function () {
            startJanus();
        }
    });
});

function startJanus() {
    log("starting Janus");

    $('#btn').click(function () {
        var button = document.getElementById("btn");

        if (started) {
            button.innerHTML = "connect";

            started = false;

            socket.close();

            socket = null;

            streamBigVideo.stop();
            streamSmallVideo.stop();

            janus = null;
        } else {
            button.innerHTML = "disconnect";

            started = true;

            socket = new WebSocket(wsPath);

            socket.onopen = function () {
                log("connected to " + wsPath);

                socket.send(JSON.stringify({client: "browser"}))
            };

            socket.onclose = function (event) {
                if (event.wasClean) {
                    log('close');
                } else {
                    log('disconnected');
                }

                log('code: ' + event.code + ' reason: ' + event.reason);
            };

            socket.onmessage = function (event) {
                // var obj = JSON.parse(event.data);
                log(event.data)
            };

            // Make sure the browser supports WebRTC
            if (!Janus.isWebrtcSupported()) {
                console.error("No webrtc support");

                return;
            }

            streamBigVideo = createVideoHandler($('#big-video'), 1);
            streamSmallVideo = createVideoHandler($('#small-video'), 2);

            // Create session
            janus = new Janus({
                server: server,
                success: function () {
                    log("Success");

                    log("Attach to streaming plugin");

                    janus.attach(streamBigVideo.attach);
                    janus.attach(streamSmallVideo.attach);
                },
                error: function (error) {
                    log(error);

                    log("janus error");
                },
                destroyed: function () {
                    log("destroyed");
                }
            });
        }


        button.blur();
    });
}

function processMessage(msg) {
    var result = msg["result"];
    if (result && result["status"]) {
        var status = result["status"];
        switch (status) {
            case 'starting':
                log("starting - please wait...");

                break;
            case 'preparing':
                log("preparing");

                break;
            case 'started':
                log("started");

                break;
            case 'stopped':
                log("stopped");

                //stopStream();

                break;
        }
    } else {
        log("no status available");
    }
}

// we never appear to get this jsep thing
function handleSDP(jsep, streaming) {
    log(" :: jsep :: ");

    log(jsep);

    if (jsep !== undefined && jsep !== null) {
        log("Handling SDP as well...");

        log(jsep);

        // Answer
        streaming.createAnswer({
            jsep: jsep,
            media: {audioSend: false, videoSend: false},      // We want recvonly audio/video
            success: function (jsep) {
                log("Got SDP!");

                log(jsep);

                var body = {"request": "start"};

                streaming.send({"message": body, "jsep": jsep});
            },
            error: function (error) {
                log("WebRTC error:");

                log(error);

                console.error("WebRTC error... " + JSON.stringify(error));
            }
        });
    } else {
        log("no sdp");
    }
}


function updateStreamsList(id, streaming) {
    var body = {"request": "list"};

    log("Sending message (" + JSON.stringify(body) + ")");

    streaming.send({
        "message": body, success: function (result) {
            if (result === null || result === undefined) {
                console.error("no streams available");
                return;
            }
            if (result["list"] !== undefined && result["list"] !== null) {
                var list = result["list"];
                log("Got a list of available streams:");

                for (var i = 0; i < list.length; i++) {
                    var stream = list[i];

                    var streamId = stream["id"];

                    if (id !== parseInt(streamId))
                        continue;

                    log("id #" + streamId + " description:" + stream["description"]);

                    log("Selected video id #" + streamId);

                    var body = {"request": "watch", id: parseInt(streamId)};

                    streaming.send({"message": body});

                    break;
                }

            } else {
                console.error("no streams available - list is null");
            }
        }
    });
}



