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
      this.$watch("roomUUID, userUUID, roomCode", () => this.saveUUIDs());
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
        localStorage.setItem("roomUUID", data.room_uuid);
        localStorage.setItem("hostUUID", data.host_uuid);
        localStorage.setItem("roomCode", data.room_code);
        this.roomUUID = data.room_uuid;
        this.hostUUID = data.host_uuid;
        this.roomCode = data.room_code;

        this.$router.push("/create"); // game has been created now we can load create screen
      });
    },
    createRoom() {
      this.socket.emit("create_room", {});
    },
    reconnect() {},
  };
}

const createRoomHandler = (socket, parent) => ({
  audio: new Audio("static/assets/awesome_music.mp3"),
  players: [],
  initialized: false,
  init() {
    console.log("create room handler");
    socket.on("player_list_update", (data) => {
      this.players = data.players;
    });
    socket.on("start_game_res", (data) => {
      if (data.status == 200) {
        console.log("Game started wooo!");
        this.$router.push("/host/" + parent.roomUUID);
      }
      console.log("start_game_res returned status " + data.status);
    });
    socket.emit("get_all_players", {
      room_uuid: parent.roomUUID,
    }); // init players list
    this.playMusic();
  },
  playMusic() {
    this.audio.play();
  },
  startGame() {
    socket.emit("start_game", { host_uuid: parent.hostUUID });
  },
});

const joinRoomHandler = (socket, parent) => ({
  code: "", // stores temp code
  name: "", // temp name
  skill: null, // stores temp skill
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
        this.$router.push(`/game/${this.name}/${parent.userUUID}`);
        return;
      }
      console.error("something has went terribly wrong ");
    });
  },
  joinRoom() {
    socket.emit("join_room", {
      name: this.name,
      code: this.code,
      skill: this.skill,
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
  setSkill(v) {
    this.skill = v;
  },
});

// player game handler
const gameHandler = (socket, parent, userUUID) => ({
  uuid: userUUID,
  gameStarted: false,
  showLeaderboard: false,
  pairings: [],
  playerPair: null,
  isBye: false,
  winSelected: null,
  init() {
    socket.on("pairings", (data) => {
      this.pairings = data.pairings;
      this.gameStarted = true;
      this.isBye = false; // reset isBye to false then check in for loop if it is a bye
      // go through every pair and find the one that is the current player's
      for (let pair of this.pairings) {
        parentLoop: for (let player of pair) {
          if (player.uuid == parent.userUUID) {
            this.playerPair = pair;
            if (pair.length == 1) {
              this.isBye = true;
            }
            break parentLoop;
          }
        }
      }
      if (this.isBye) {
        this.winSelected = "bye";
        this.submitGameResult();
      }
      // remove that pair from the list and add it to the front
      this.pairings = this.pairings.filter((i) => i !== this.playerPair);
      this.pairings.unshift(this.playerPair);
      addModalListeners(); // add the closing events such as pressing escape, clicking the close button, or clicking anywhere other than the modal
    });

    socket.on("game_result_res", (data) => {
      if (data.status === 200) {
        this.showLeaderboard = true;
      }
    });
  },
  submitGameResult() {
    // close the modal
    closeAllModals();
    socket.emit("game_result", {
      room_uuid: parent.roomUUID,
      player_uuid: parent.userUUID,
      result: this.winSelected, // the winner
    });
  },
});

// DEFAULT BULMA IMPLEMENTATION FOR MODALS - CAN IGNORE
// Functions to open and close a modal
function openModal($el) {
  $el.classList.add("is-active");
}

function closeModal($el) {
  $el.classList.remove("is-active");
}

function closeAllModals() {
  (document.querySelectorAll(".modal") || []).forEach(($modal) => {
    closeModal($modal);
  });
}

function addModalListeners() {
  // Add a click event on buttons to open a specific modal
  (document.querySelectorAll(".js-modal-trigger") || []).forEach(($trigger) => {
    const modal = $trigger.dataset.target;
    const $target = document.getElementById(modal);

    $trigger.addEventListener("click", () => {
      openModal($target);
    });
  });

  // Add a click event on various child elements to close the parent modal
  (
    document.querySelectorAll(
      ".modal-background, .modal-close, .modal-card-head .delete, .modal-card-foot .button"
    ) || []
  ).forEach(($close) => {
    const $target = $close.closest(".modal");

    $close.addEventListener("click", () => {
      closeModal($target);
    });
  });
}
// Add a keyboard event to close all modals
document.addEventListener("keydown", (event) => {
  const e = event || window.event;

  if (e.keyCode === 27) {
    // Escape key
    closeAllModals();
  }
});
