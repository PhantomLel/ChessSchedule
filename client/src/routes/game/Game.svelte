<script lang="ts">
    import { onDestroy, onMount } from "svelte";
    import { Route, Router } from "svelte-routing";
    import { ws, roomUUID } from "../../ws";
    import { fly } from "svelte/transition";

    // storing the uuid and name in the url allows for mulptiple
    // games to be played at once
    export let uuid;
    export let name;

    onMount(() => {
        ws.on("reconnect_player_res", (data) => {
            switch(data.room_state) {
                case "wait":
                    break;
            }
        });

        ws.on("room_exists", (data) => {
            if (!data.exists) {
                window.location.href = "/join/code";
            }

            // reconnect
            ws.emit("reconnect_player", {
                room_uuid: $roomUUID,
                player_uuid: uuid,
            });
        });

        ws.on("game_ended", () => {
            window.location.href = "/join/code";
        });

        ws.emit("room_exists", {
            room_uuid: $roomUUID,
        });

    });
    onDestroy(() => {
        ws.off("reconnect_player_res");
        ws.off("room_exists");
    });
</script>

<Router>
    <main class="hero is-fullheight has-text-centered">
        <div class="hero-body">
            <div class="container">
                <Route path="waiting">
                    <h1 in:fly={{ x: 1000, duration: 1000 }} class="title is-2">
                        Hey {name}, waiting for other players to join...
                    </h1>
                </Route>
                
            </div>
        </div>
    </main>
</Router>
