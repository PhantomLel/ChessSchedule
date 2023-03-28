<script lang="ts">
  import { onDestroy, onMount } from "svelte";
  import { ws, getLeaderboard } from "../../ws";

  let players: { name: string; score: number[] }[] = [];
  let round: number;

  onMount(() => {
    ws.on("leaderboard", (data) => {
      players = data.rankings;
    });

    ws.on("pairings", (data) => {
      round = data.round;
    });
    getLeaderboard();
  });

  onDestroy(() => {
    ws.off("leaderboard");
    ws.off("pairings")
  });
</script>

<section class="box my-6 mx-2 leaderboard admin column is-half">
  <div>
    <h1 class="title is-size-2">Leaderboard</h1>
    <h2 class="title is-size-4">Round {round}</h2>
    <hr />
  </div>
  <table class="table">
    <thead>
      <tr>
        <th>Name</th>
        <th>Wins</th>
        <th>Draws</th>
        <th>Losses</th>
        <th>ELO</th>
      </tr>
    </thead>

    <tbody>
      {#each players as player}
        <tr>
          <td>{player.name}</td>
          <td>{player.score[0]}</td>
          <td>{player.score[1]}</td>
          <td>{player.score[2]}</td>
          <td>{player.score[3]}</td>
        </tr>
      {/each}
    </tbody>
  </table>
</section>
