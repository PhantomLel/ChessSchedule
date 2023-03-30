<script lang="ts">
  import { onDestroy } from "svelte";
  import { fly } from "svelte/transition";
  import { roomUUID, ws } from "../../ws";

  export let uuid: string;
  export let pairings: { name: string; uuid: string }[][] = [];
  export let name : string;

  let currentPair: { name: string; uuid: string }[];
  let isBye = false;
  let gameSubmitted = false;
  let statusMsg = "";

  // reset some variables back to default
  gameSubmitted = false;
  statusMsg = "";

  ws.on("game_result_res", (data) => {
    if (data.status == 200) {
      statusMsg = "Game result confirmed!";
    } else {
      statusMsg = "Game result did not match with opponent. Please try again.";
      gameSubmitted = false;
    }
  });

  const submitGameResult = (result: string) => {
    ws.emit("game_result", {
      room_uuid: $roomUUID,
      player_uuid: uuid,
      result,
    });
    gameSubmitted = true;
    statusMsg = "Game submitted. Waiting for other player's response";
  };

  const handlePairings = (pairings) => {
    // get the current pair
    for (let pair of pairings) {
      for (let player of pair) {
        if (player.uuid == uuid) {
          currentPair = pair;
        }
      }
    }

    isBye = currentPair.length == 1;
    // put the user's name first in the list
    if (!isBye && currentPair[0].uuid != uuid) {
      let temp = currentPair[0];
      currentPair[0] = currentPair[1];
      currentPair[1] = temp;
    }

    // if bye, submit the game
    if (isBye) {
      submitGameResult("bye");
    }
  };
  onDestroy(() => {
    ws.off("game_result_res");
  });

  // handle the state that the player is in currently on reconnect
  export const handlePlayerState = (state) => {
    console.log(state, "state");
    switch (state) {
      case "inconclusive":
        break;
      case "awaiting":
        gameSubmitted = true;
        statusMsg = "Game submitted. Waiting for other player's response.";
        break;
      case "submitted":
        gameSubmitted = true;
        statusMsg = "";
        statusMsg = "Game result confirmed!";
    }
  };

  // reactivly get the current pair
  $: handlePairings(pairings);
</script>

<div class="columns is-centered is-vcentered">
  <div class="column is-three-fourths">
    <div in:fly={{x:500}} class="title is-size-3">Good Luck {name}!</div>
    {#if !isBye && currentPair}
      <!-- show the opponent if not submitted yet -->
      {#if !statusMsg}
        <div in:fly={{ y: -400, delay: 100 }} class="title is-size-2">
          Opponent for this round: {currentPair[1].name}
        </div>
      {:else}
        <div class="title is-size-2">
          {statusMsg}
        </div>
      {/if}
      <!-- game res buttons  -->
      <button
        disabled={gameSubmitted}
        on:click={() => {
          submitGameResult(currentPair[0].uuid);
        }}
        in:fly={{ x: -400, delay: 430 }}
        class="button is-large my-4 mx-2 is-primary">You won</button
      >
      <button
        disabled={gameSubmitted}
        on:click={() => submitGameResult("draw")}
        in:fly={{ y: 500, delay: 280 }}
        class="button is-large my-4 mx-2 is-dark">Draw</button
      >
      <button
        disabled={gameSubmitted}
        on:click={() => submitGameResult(currentPair[1].uuid)}
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
