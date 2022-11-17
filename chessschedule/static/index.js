function socketManager() {
  return {
    parent: null, // so that it can be accessed by other managers
    socket: null,
    roomUUID: null, // either will be undefined or the actaul uuid's
    userUUID: null,
    roomCode: null,
    init() {
      this.parent = this;
      this.socketBuilder(); // create socket
      this.roomUUID = localStorage.getItem("roomUUID");
      this.userUUID = localStorage.getItem("userUUID");
      this.roomCode = localStorage.getItem("roomCode");
    },
    socketBuilder() {
      this.socket = io();
      this.socket.on("connect", () => {
        console.log("Connected");
      });
      this.socket.on("create_room_res", (data) => {
        localStorage.setItem("roomUUID", data.room_uuid);
        localStorage.setItem("userUUID", data.user_uuid);
        localStorage.setItem("roomCode", data.room_code);
        this.roomUUID = data.room_uuid;
        this.userUUID = data.user_uuid;
        this.roomCode = data.room_code;
      });
    },
    createRoom() {
      this.socket.emit("create_room", {});
    },
    reconnect() {},
  };
};
