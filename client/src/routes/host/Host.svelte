<script lang="ts">
  import Pairings from "./Pairings.svelte";
  import Leaderboard from "./Leaderboard.svelte";
  import { onDestroy, onMount } from "svelte";
  import { ws, roomUUID, hostUUID, getLeaderboard } from "../../ws";

  let pairings: { name: string; uuid: string }[][] = [];

  onMount(() => {
    ws.on("pairings", (data) => {
      pairings = data.pairings;
      getLeaderboard();
    });
    ws.on("reconnect_host_res", (data) => {
      ws.emit("get_pairings", {
        room_uuid: $roomUUID,
      });
    });
    ws.on("game_ended", () => {
      roomUUID.set("");
      hostUUID.set("");
      window.location.href = "/";
    });

    ws.emit("reconnect_host", {
      room_uuid: $roomUUID,
      host_uuid: $hostUUID,
    });
  });

  onDestroy(() => {
    ws.off("pairings");
    ws.off("reconnect_host_res");
  });

  const nextRound = () => {
    ws.emit("next_round", {
      room_uuid : $roomUUID,
      host_uuid : $hostUUID,
      ensure_match_completions : false,
    });
  }

  export const endGame = () => {
    if (!confirm("Are you sure you want to end the game?")) return;
    ws.emit("end_game_host", {
      room_uuid: $roomUUID,
      host_uuid: $hostUUID,
    });
  };
</script>

<main>
  <div class="columns is-centered has-text-centered mx-4">
    <Pairings {pairings} />
    <div class="column is-half">
      <Leaderboard/>
    </div>
  </div>
  <div class="columns">
    <div class="column">
      <div class="buttons are-medium is-centered">
        <button on:click={nextRound} class="button is-primary table"> Next Round </button>
        <button on:click={endGame} class="button is-danger table">
          End Game
        </button>
      </div>
    </div>
  </div>
</main>
