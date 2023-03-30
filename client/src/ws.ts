import { io, Socket } from "socket.io-client";
import { writable } from "svelte/store";

// create ws connection and export it
const ws: Socket = io(window.location.origin, {
    transports: ['websocket']  // forces websockets only
  }
);
ws.on("connect", () => {
  console.log("connected");
});

const roomUUID = writable("");
const userUUID = writable("");
const hostUUID = writable("");
const roomCode = writable("");

// get them from local storage on load
roomUUID.set(localStorage.getItem("roomUUID") || "");
userUUID.set(localStorage.getItem("userUUID") || "");
hostUUID.set(localStorage.getItem("hostUUID") || "");
roomCode.set(localStorage.getItem("roomCode") || "");

// save them all to local storage on change
roomUUID.subscribe((value) => {
  localStorage.setItem("roomUUID", value);
});
userUUID.subscribe((value) => {
  localStorage.setItem("userUUID", value);
});
hostUUID.subscribe((value) => {
  localStorage.setItem("hostUUID", value);
});
roomCode.subscribe((value) => {
  localStorage.setItem("roomCode", value);
});

export function getLeaderboard() {
  ws.emit("get_leaderboard", { room_uuid: localStorage.getItem("roomUUID")});
}

export { ws, roomUUID, userUUID, hostUUID, roomCode };
