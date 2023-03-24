import type { Socket } from "socket.io";
import { io } from "socket.io-client";

let ws = null;

const initWebsocket = () => {
    if (ws == null) {
        ws = io();
    }
}

export {ws, initWebsocket};