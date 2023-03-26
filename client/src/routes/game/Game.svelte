<script lang="ts">
    import { onDestroy, onMount } from "svelte";
    import { Route, Router } from "svelte-routing";
    import { ws } from "../../ws";

    // storing the uuid and name in the url allows for mulptiple
    // games to be played at once
    export let uuid;
    export let name;

    onMount(() => {
        ws.on("game_ended", () => {
            window.location.href = "/join";
        });
    });
    onDestroy(() => {
        ws.off("game_ended");
    });
</script>

<Router>
    <main class="hero is-fullheight has-text-centered">
        <div class="hero-body">
            <div class="container">
                <Route path="waiting">
                    <h1 class="title is-2">
                        Hey {name}, waiting for other players to join...
                    </h1>
                </Route>
            </div>
        </div>
    </main>
</Router>
