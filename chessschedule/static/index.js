
const socketBuilder = () => {
    var socket = io();
    socket.on('connect', () => {
        console.log("Connected");
    });
    socket.on('create_room_res', (data) => {
        localStorage.setItem('roomUUID', data.room_uuid);
        localStorage.setItem('userUUID', data.user_uuid);
        localStorage.setItem('roomCode', data.room_code);
    });

    return socket;
}

function socketManager () {
    return {
        socket: null,
        roomUUID: null, // either will be undefined or the actaul uuid's
        userUUID: null,
        roomCode: null,
        init() {
            this.socket = socketBuilder();
            this.roomUUID = localStorage.getItem('roomUUID');
            this.userUUID= localStorage.getItem('userUUID');
            this.roomCode = localStorage.getItem('roomCode');

        },
        createRoom() {
            this.socket.emit('create_room', {});
        },
        reconnect() {

        }
    }
}