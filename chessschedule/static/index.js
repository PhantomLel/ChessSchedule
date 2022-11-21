
function socketManager() {
  return {
    parent: null, // so that it can be accessed by other managers
    socket: null,
    roomUUID: null, // either will be undefined or the actaul uuid's
    userUUID: null,
    hostUUID: null,
    roomCode: null,
    init() {
      this.parent = this;
      this.socketBuilder(); // create socket
      this.roomUUID = localStorage.getItem("roomUUID");
      this.userUUID = localStorage.getItem("userUUID");
      this.roomCode = localStorage.getItem("roomCode");
      this.hostUUID = localStorage.getItem("hostUUID");
      // if uuids change, save them to localstorage
      this.$watch("roomUUID, userUUID, roomCode, hostUUID", () =>
        this.saveUUIDs()
      );
    },
    saveUUIDs() {
      // store in case user becomes disconnected
      localStorage.setItem("roomUUID", this.roomUUID);
      localStorage.setItem("hostUUID", this.hostUUID);
      localStorage.setItem("roomCode", this.roomCode);
      localStorage.setItem("userUUID", this.userUUID);
    },
    socketBuilder() {
      this.socket = io();
      this.socket.on("connect", () => {
        console.log("Connected");
      });
      this.socket.on("create_room_res", (data) => {
        console.log(data);
        localStorage.setItem("roomUUID", data.room_uuid);
        localStorage.setItem("hostUUID", data.user_uuid);
        localStorage.setItem("roomCode", data.room_code);
        this.roomUUID = data.room_uuid;
        this.userUUID = data.user_uuid;
        this.roomCode = data.room_code;

        this.$router.push("/create") // game has been created now we can load create screen
      });
    },
    createRoom() {
      this.socket.emit("create_room", {});
    },
    reconnect() {},
  };
}

const createRoomHandler = (socket, parent) => (
  {
    audio : new Audio('static/assets/awesome_music.mp3'),
    players : [],
    initialized : false,
    init() {
      console.log("create room handler")
      socket.on("player_list_update", (data) => {
        console.log(this.players);
        this.players = data.players;
      });
      socket.emit("get_all_players", {
        room_uuid : parent.roomUUID
      }); // init players list
      this.playMusic();
    },
    playMusic() {
      this.audio.play();
    }
  }
)

const joinRoomHandler = (socket, parent) => ({
  code: "", // stores temp code
  name: "", // temp name
  validName: false,
  error: "",
  joinedRoom: false,
  init() {
    socket.on("check_room_res", (data) => {
      // room does not exist
      if (data.error) {
        this.error = data.error;
        return;
      }
      parent.roomUUID = data.room_uuid;
      // switch to name input
      this.error = "";
      this.joinedRoom = true;
    });

    socket.on("check_name_res", (data) => {
      if (!data.valid) {
        this.error = "Name Invalid or Taken";
      } else {
        this.error = "";
      }
      this.validName = data.valid;
    });

    socket.on("join_room_res", (data) => {
      if (!data.error) {
        parent.userUUID = data.user_uuid;
        // go to /game as we have successfully connected to a room
        this.$router.push("/game");
      }
      console.error("something has went terribly wrong ");
    });
  },
  joinRoom() {
    socket.emit("join_room", {
      name: this.name,
      code: this.code
    });
  },
  checkCode() {
    if (this.code.length != 7) {
      this.error = "Code must be 7 digits long";
      return;
    }
    socket.emit("check_room", { code: this.code });
  },
  checkName() {
    socket.emit("check_name", { name: this.name, room_uuid: parent.roomUUID });
  },
});

const gameHandler = (socket, parent) => {
  {
  }
};
