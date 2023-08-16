<script lang="ts">
  import { onDestroy, onMount, tick } from "svelte";
  import { ws } from "../ws";
  import { roomUUID, hostUUID, roomCode } from "../ws";
  import { tooltip } from "@svelte-plugins/tooltips";
  import { navigate } from "svelte-routing";

  let players: { name: string; rating: number; uuid: string }[] = [];
  let audio = new Audio("static/assets/awesome_music.mp3");
  let isModalActive = false;

  let playerStaging: string[] = [""];

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

    ws.on("start_game_res", (data) => {
      if (data.status == 200) {
        navigate("/host");
      }
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
    ws.off("start_game_res");

    audio.pause();
  });

  const closeModal = () => {
    isModalActive = false;
  };

  const startGame = () => {
    if (!confirm(`Start game with ${players.length} players?`)) return;
    ws.emit("start_game", { host_uuid: $hostUUID });
  };

  const cancelGame = () => {
    if (!confirm("Are you sure you want to cancel this game?")) return;
    ws.emit("end_game_host", {
      room_uuid: $roomUUID,
      host_uuid: $hostUUID,
    });
  };

  const removePlayer = (uuid: string) => {
    ws.emit("remove_player", {
      room_uuid: $roomUUID,
      host_uuid: $hostUUID,
      player_uuid: uuid,
    });
  };

  const addPlayer = (name: string) => {
    ws.emit("join_room", {
      room_uuid: $roomUUID,
      name,
      skill: 3
    });
  };
</script>

<main>
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
      <span class="title is-size-3">Players: {players.length}</span>
      <br />
      <button
        on:click={startGame}
        disabled={players.length < 2}
        class="button is-primary is-large start-btn">Start Tournament</button
      >
      <button
        on:click={() => (isModalActive = true)}
        class="button is-info is-large start-btn"
      >
        Add Players
      </button>
      <button
        on:click={cancelGame}
        class="button is-danger is-outlined is-large start-btn">Cancel</button
      >
    </div>
  </div>
  <div class="columns is-multiline is-centered">
    {#each players as player}
      <div use:tooltip title={player.rating} class="player-tile">
        {player.name}
        <button
          on:click={() => removePlayer(player.uuid)}
          class="delete ml-2"
        />
      </div>
    {/each}
  </div>
</main>

<div class="modal" class:is-active={isModalActive}>
  <div class="modal-background" on:keydown={null} on:click={closeModal}></div>
  <div class="modal-card m-4">
    <header class="modal-card-head">
      <p class="modal-card-title">
        Add Players
      </p>
      <button use:tooltip={{position:"bottom", content: "This will add headless players who are unable to connect via a device. You will have to manually enter their results."}} class="button is-info is-rounded mr-4 has-text-weight-bold">?</button>
      <button class="delete" on:click={closeModal} aria-label="close"></button>
    </header>
    <section class="modal-card-body">
    {#each playerStaging as inp, i}
      <div class="field has-addons">
        <div class="control is-expanded">
          <input
            bind:value={playerStaging[i]}
            class="input is-medium"
            type="text"
            maxlength=16
            placeholder="Player Name"
            on:keydown={async (e) => {
              // on enter, add a new input and switch focus to it
              if (e.key === "Enter") {
                playerStaging = [...playerStaging, ""];
                await tick();
                const inputs = document.querySelectorAll("input");
                inputs[inputs.length - 1].focus();
              }
              // opposite on backspace
              if (e.key == "Backspace" && inp === "" && i !== 0) {
                playerStaging = playerStaging.filter((_, index) => index !== i);
                await tick();
                const inputs = document.querySelectorAll("input");
                inputs[inputs.length - 1].focus();
              }
            }}
          />
        </div>
        <div class="control">
          <button 
            on:click={() => {
              if (playerStaging.length === 1) {
                playerStaging = [""]; 
                return;
              }
              playerStaging = playerStaging.filter((_, index) => index !== i);
            }}
            class="button is-danger is-light is-medium">Remove  </button>
        </div>
      </div>
    {/each}
    </section>
    <footer class="modal-card-foot">
      <button on:click={closeModal} class="button">Cancel</button>
      <button disabled={
        playerStaging.length === 0 || 
        // names must be at least 3 characters long
        playerStaging.some((p) => p.length < 3) || 
        // names must be unique 
        playerStaging.some((p) => players.some((pl) => pl.name === p)) ||
        // names must be unqiue to each other
        playerStaging.some((p, i) => playerStaging.some((pl, j) => p === pl && i !== j))
      } 
      on:click={() => {
        playerStaging.forEach((p) => addPlayer(p));
        playerStaging = [""];
        closeModal(); 
      }}
      class="button is-success">Add</button>
    </footer>
  </div>
</div>