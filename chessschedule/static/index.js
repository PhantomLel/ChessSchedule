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
      localStorage.setItem("roomCode", this.roomCode);
      if (this.$router.path === "/create") {
        localStorage.setItem("hostUUID", this.hostUUID);
      }
      if (
        this.$router.path.startsWith("/join") ||
        this.$router.path.startsWith("/game")
      ) {
        localStorage.setItem("userUUID", this.userUUID);
      }
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
    // disconnect handler
    this.socket.on("disconnect", () => {
      var interval = setInterval(() => {
        this.socket.connect();
        if (this.socket.connected) {
          this.reconnect();
          // stop the reconnection
          clearInterval(interval);
        }
      }, 1000);
    });
    socket.on("reconnect_host_res", (data) => {
      socket.emit("get_all_players", {
        room_uuid: parent.roomUUID,
      });
    });
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

    socket.on("disconnect", () => {
      console.log("Disconnected");
    });
    this.playMusic();
    // get new players and stuff
    this.reconnect();
  },
  playMusic() {
    this.audio.play();
  },
  startGame() {
    socket.emit("start_game", { host_uuid: parent.hostUUID });
  },
  reconnect() {
    console.log("Attempting Reconnect");
    socket.emit("reconnect_host", {
      room_uuid: parent.roomUUID,
      host_uuid: parent.hostUUID,
    });
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
  gameSubmitted: false,
  pairings: [],
  playerPair: null,
  isBye: false,
  winSelected: null,
  async init() {
    // disconnect handler
    this.socket.on("disconnect", () => {
      var interval = setInterval(() => {
        this.socket.connect();
        if (this.socket.connected) {
          this.reconnect();
          // stop the reconnection
          clearInterval(interval);
        }
      }, 1000);
    });
    socket.on("pairings", (data) => {
      this.pairings = data.pairings;
      this.resetVars();
      this.extractData();
      this.gameStarted = true;
      // reset to defaults

      if (this.isBye) {
        this.winSelected = "bye";
        this.submitGameResult();
      }
      // remove that pair from the list and add it to the front
      addModalListeners(); // add the closing events such as pressing escape, clicking the close button, or clicking anywhere other than the modal
    });
    socket.on("game_result_res", (data) => {
      if (data.status === 200) {
        this.$refs.gameSubmitMsg.innerText =
          "Game Result Has Been Confirmed By Your Opponent";
      } else {
        console.warn("Win selection failed. Reprompting");
        // reset who is selected
        this.winSelected = null;
        this.gameSubmitted = false;
        openModal(this.$refs.selectModal);
      }
    });

    // this event indicates the end of this round
    socket.on("round_results", (data) => {
      this.showLeaderboard = true;
    });

    socket.on("game_ended", (data) => {
      // go to results page
      this.$router.push("/results/" + JSON.stringify(data.results));
    });

    socket.on("get_pairings_res", (data) => {
      this.pairings = data.pairings;
      this.extractData();
    });

    socket.on("reconnect_player_res", async (data) => {
      console.log(data.room_state, data.player_state);
      switch (data.room_state) {
        case "wait":
          break;
        case "pairings":
          this.socket.emit("get_pairings", { room_uuid: parent.roomUUID });
          this.gameStarted = true;
          // wait for alpine to refresh components
          await this.$nextTick();
          switch (data.player_state) {
            case "inconclusive":
              break;
            case "awaiting":
              this.gameSubmitted = true;
              this.$refs.gameSubmitMsg.innerText =
                "Game Result Submitted. Waiting for other player.";
              break;
            case "submitted":
              this.gameSubmitted = true;
              this.$refs.gameSubmitMsg.innerText =
                "Game Result Has Been Confirmed By Your Opponent";
              break;
          }
          break;
        case "leaderboard":
          this.gameStarted = true;
          this.gameSubmitted = true;
          this.showLeaderboard = true;
          break;
      }
    });

    this.reconnect();
  },
  submitGameResult() {
    // close the modal
    closeAllModals();
    socket.emit("game_result", {
      room_uuid: parent.roomUUID,
      player_uuid: this.$router.params.userUUID,
      result: this.winSelected, // the winner
    });
    this.gameSubmitted = true;
    // change the msg to indicate status
    this.$refs.gameSubmitMsg.innerText =
      "Game Result Submitted. Waiting for other player.";
  },
  // gets this.playerPair and this.isBye from this.pairings
  extractData() {
    // go through every pair and find the one that is the current player's
    for (let pair of this.pairings) {
      parentLoop: 
      for (let player of pair) {
        if (player.uuid == this.$router.params.userUUID) {
          this.playerPair = pair;
          if (pair.length == 1) {
            this.isBye = true;
          }
          break parentLoop;
        }
      }
    }
    // remove playerPair and add it to beginning of the pairings list
    // this.pairings = this.pairings.filter((i) => i !== this.playerPair);
    // this.pairings.unshift(this.playerPair);
  },
  // reset all the vars to default
  resetVars() {
    this.isBye = false;
    this.showLeaderboard = false;
    this.gameSubmitted = false;
    this.winSelected = null;
    this.playerPair = null;
  },
  reconnect() {
    socket.emit("reconnect_player", {
      room_uuid: parent.roomUUID,
      player_uuid: this.$router.params.userUUID,
    });
  },
});

const hostHandler = (socket, parent) => ({
  pairings: [],
  leaderboard: leaderboardHandler(socket, parent),
  init() {
    socket.on("pairings", (data) => {
      this.pairings = data.pairings;
      this.leaderboard.getLeaderboard();
    });
    socket.on("get_pairings_res", (data) => {
      this.pairings = data.pairings;
      this.leaderboard.getLeaderboard();
    });

    // response to end_game_host
    socket.on("game_ended", (data) => {
      // go to results page
      this.$router.push("/results/" + JSON.stringify(data.results));
    });
    this.socket.on("reconnect_host_res", (data) => {
      this.socket.emit("get_pairings", { room_uuid: parent.roomUUID });
    });
    this.reconnect();
    // disconnect handler
    this.socket.on("disconnect", () => {
      var interval = setInterval(() => {
        this.socket.connect();
        if (this.socket.connected) {
          this.reconnect();
          // stop the reconnection
          clearInterval(interval);
        }
      }, 1000);
    });
  },
  nextRound() {
    socket.emit("next_round", {
      room_uuid: parent.roomUUID,
      host_uuid: parent.hostUUID,
      // TODO ask the host if they want to do this or not
      ensure_match_completions: false,
    });
    this.leaderboard.getLeaderboard();
  },
  endGame() {
    socket.emit("end_game_host", {
      room_uuid: parent.roomUUID,
      host_uuid: parent.hostUUID,
    });
  },
  reconnect() {
    console.log("Attempting Reconnect");
    socket.emit("reconnect_host", {
      room_uuid: parent.roomUUID,
      host_uuid: parent.hostUUID,
    });
  },
});

const leaderboardHandler = (socket, parent) => ({
  players: [],
  init() {
    socket.on("leaderboard", (data) => {
      this.players = data.rankings;
    });
    this.getLeaderboard();
  },
  getLeaderboard() {
    socket.emit("get_leaderboard", { room_uuid: parent.roomUUID });
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
