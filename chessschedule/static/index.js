var socket = io();
socket.on('connect', () => {
    console.log("Connected!");
    socket.emit('my event', {msg : "even cooler msg"});
});

socket.on('wow', (data) => {
    console.log(data.nicemsg);
});
