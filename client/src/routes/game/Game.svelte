<script lang="ts">
  import { onDestroy, onMount, tick } from "svelte";
  import { navigate, Route, Router } from "svelte-routing";
  import { ws, roomUUID, userUUID } from "../../ws";
  import { fade, fly } from "svelte/transition";
  import Pairings from "./Pairings.svelte";
  import Leaderboard from "../host/Leaderboard.svelte";

  // storing the uuid and name in the url allows for mulptiple
  // games to be played at once
  export let uuid: string;
  export let name: string;


  let pairingComp;
  let pairings: { name: string; uuid: string }[][] = [];

  onMount(() => {
    ws.on("reconnect_player_res", async (data) => {
      switch (data.room_state) {
        case "wait":
          navigate(`/game/${name}/${uuid}/waiting`, { replace: true });
          break;
        case "pairings":
          ws.emit("get_pairings", {
            room_uuid: $roomUUID,
          });
          await tick();
          // only handle the state if client is already on /pairings route
          if (pairingComp != null) {
            pairingComp.handlePlayerState(data.player_state);
          }
          await tick();
          break;
        case "leaderboard":
          navigate(`/game/${name}/${uuid}/leaderboard`, { replace: true });
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

    ws.on("pairings", async (data) => {
      pairings = data.pairings;
      await tick();
      navigate(`/game/${name}/${uuid}/pairings`, { replace: true });
    });

    ws.on("round_results", () => {
      navigate(`/game/${name}/${uuid}/leaderboard`, { replace: true });
    });

    // listen if the client has been kicked from the game
    ws.on("player_removed", (data) => {
      if (uuid == data.uuid) {
        alert("You have been kicked from this game. Please try joining again.");
        roomUUID.set("");
        navigate("/");
      }
    });

    ws.on("game_ended", () => {
      window.location.href = "/join/code";
    });
  });
  onDestroy(() => {
    ws.off("reconnect_player_res");
    ws.off("room_exists");
    ws.off("pairings");
    ws.off("game_ended");
    ws.off("player_removed")
  });

  ws.emit("room_exists", {
    room_uuid: $roomUUID,
  });
</script>

<Router>
  <main class="hero is-fullheight has-text-centered">
    <div class="hero-body">
      <div class="container">
        <Route path="waiting">
          <h1 in:fly={{ x: 1000, duration: 1000 }} out:fade class="title is-2">
            Hey {name}, waiting for other players to join!
          </h1>
        </Route>
        <Route path="pairings">
          <Pairings bind:this={pairingComp} {name} {pairings} {uuid} />
        </Route>
        <Route path="leaderboard" component={Leaderboard}></Route>
      </div>
    </div>
  </main>
</Router>