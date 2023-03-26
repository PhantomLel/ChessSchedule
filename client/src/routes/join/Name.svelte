<script lang="ts">
    import { onDestroy, onMount } from "svelte";
    import { roomUUID, ws } from "../../ws";
    import { tooltip } from "@svelte-plugins/tooltips";
    import {debounce} from "lodash";

    const BUTTONS = [
        { name: "pawn", tip: "Novice", img: "static/assets/pawn.png" },
        { name: "knight", tip: "Amateur", img: "static/assets/knight.png" },
        {
            name: "bishop",
            tip: "Intermediate",
            img: "static/assets/bishop.png",
        },
        { name: "rook", tip: "Advanced", img: "static/assets/rook.png" },
        { name: "queen", tip: "Master", img: "static/assets/queen.png" },
    ];

    let nameInp: HTMLInputElement;

    onMount(() => {
        // focus on input
        nameInp.focus();

        ws.on("check_name_res", (data) => {
            if (!data.valid) {
                error = "Name Invalid or Taken";
            } else {
                error = "";
            }
            validName = data.valid;
        });
    });

    onDestroy(() => {
        ws.off("check_name_res");
    });

    let name = "";
    let error = "";
    let skill: number = null;
    let validName = false;

    const checkName = debounce(() =>{
        ws.emit("check_name", { name: name, room_uuid: $roomUUID });
    }, 500);
</script>

<main>
    <p class="block is-size-2">Enter Your Name</p>
    <div class="join-input block">
        <input
            on:keyup={checkName}
            bind:this={nameInp}
            bind:value={name}
            class="input is-large"
            placeholder="Jason Quang"
            maxlength="14"
        />
    </div>
    <p class="block is-size-2">Select Skill Level</p>
    <div class="skill-input block">
        {#each BUTTONS as { name, tip, img }, i}
            <button
                class="button"
                class:is-focused={skill == i}
                on:click={() => (skill = i)}
                use:tooltip
                title={tip}
            >
                <img src={img} alt={name} />
            </button>
        {/each}
    </div>

    <!-- error variable is reused for both forms -->
    <span class="error-msg">{error}</span>

    <div class="block">
        <button
            disabled={name.length < 3 || !validName || skill === null}
            class="mt-4 button is-primary is-large"
        >
            Join
        </button>
    </div>
</main>
