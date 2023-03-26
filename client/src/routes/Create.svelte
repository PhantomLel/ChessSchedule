<script lang="ts">
    import { onDestroy, onMount } from "svelte";
    import { ws } from "../ws";
    import { roomUUID, hostUUID, roomCode } from "../ws";
    import { tooltip } from "@svelte-plugins/tooltips";

    let players: { name: string; rating: number }[] = [];
    let audio = new Audio("static/assets/awesome_music.mp3");

    onMount(() => {
        ws.on("create_room_res", (data) => {
            roomUUID.set(data.room_uuid);
            hostUUID.set(data.host_uuid);
            roomCode.set(data.room_code);
        });

        ws.on("game_ended", () => {
            roomUUID.set("");
            hostUUID.set("");
            roomCode.set("");

            window.location.href = "/";
        });

        ws.on("reconnect_host_res", (data) => {
            ws.emit("get_all_players", {
                room_uuid: $roomUUID,
            });
        });

        ws.on("player_list_update", (data) => {
            players = data.players;
        });

        ws.on("room_exists", (data) => {
            if (data.exists) {
                ws.emit("reconnect_host", {
                    room_uuid: $roomUUID,
                    host_uuid: $hostUUID,
                });
            } else {
                // if room does not exist, create a new room
                ws.emit("create_room", {});
            }
        });

        // if the user has already created a room that has not been closed yet
        if ($roomUUID === "") {
            ws.emit("create_room", {});
        } else {
            ws.emit("room_exists", {
                room_uuid: $roomUUID,
            });
        }

        audio.play();
    });

    onDestroy(() => {
        ws.off("create_room_res");
        ws.off("game_ended");
        ws.off("reconnect_host_res");
        ws.off("player_list_update");
        ws.off("room_exists");
        
        audio.pause();

    });

    const cancelGame = () => {
        if (!confirm("Are you sure you want to cancel this game?")) return;
        ws.emit("end_game_host", {
            room_uuid: $roomUUID,
            host_uuid: $hostUUID,
        });
    };
</script>

<main class="">
    <div class="columns is-centered has-text-centered">
        <div class="column">
            <div>
                {#if $roomCode === ""}
                    <h1 class="join-code">Loading</h1>
                {:else}
                    <h1 class="join-code">{$roomCode}</h1>
                {/if}
            </div>
            <br />
            <span class="is-size-2">Join Code</span>
            <br />
            <button
            disabled={players.length < 2}
            class="button is-primary is-large start-btn"
                >Start Tournament</button
            >
            <button
                on:click={cancelGame}
                class="button is-danger is-outlined is-large start-btn"
                >Cancel</button
            >
            <hr />
        </div>
    </div>
    <div class="columns is-multiline is-centered">
        {#each players as player}
            <h1 use:tooltip title={player.rating} class="player-tile">
                {player.name}
            </h1>
        {/each}
    </div>
</main>
