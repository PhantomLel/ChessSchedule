<script lang="ts">
  import { fly } from "svelte/transition";
  import { ws } from "../../ws";

  export let uuid: string;
  export let pairings: { name: string; uuid: string }[][] = [];

  ws.on("pairings", (data) => {
    pairings = data.pairings;
  });
  let currentPair: { name: string; uuid: string }[];
  let isBye : boolean = false;
  $: {
    for (let pair of pairings) {
      for (let player of pair) {
        if (player.uuid == uuid) {
          currentPair = pair;
        }
      }
    }

    isBye = currentPair.length == 1;
    // put the user's name first in the list
    if (!isBye && currentPair[1].uuid == uuid) {
      let temp = currentPair[0];
      currentPair[0] = currentPair[1];
      currentPair[1] = temp;
    }
  }
</script>

<div class="columns is-centered is-vcentered">
  <div class="column is-three-fourths">
    {#if !isBye}
      <div in:fly={{ y: 300, delay: 100 }} class="title is-size-2">
        Opponent for this round: {currentPair[1].name}
      </div>
      <button
        in:fly={{ x: -400, delay: 350 }}
        class="button is-large my-4 mx-2 is-primary">You won</button
      >
      <button
        in:fly={{ x: 400, delay: 200 }}
        class="button is-large my-4 mx-2 is-danger">Oppponent Won</button
      >
    {:else}
      <div in:fly={{ y: 400, delay: 200 }} class="title is-size-1">
        Sitout this round :(
      </div>
    {/if}
  </div>
</div>
