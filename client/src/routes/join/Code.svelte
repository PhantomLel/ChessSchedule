<script lang="ts">
    import { roomUUID, ws } from "../../ws";
    import { onDestroy, onMount } from "svelte";
    import { navigate } from "svelte-routing";
    import { fade, fly } from "svelte/transition";
    let error = "";
    let code = "";
    let inp : HTMLInputElement;
    // add ws event listeners in onmount
    onMount(() => {
        inp.focus();
        ws.on("check_room_res", (data) => {
            if (data.error) {
                error = data.error;
            } else {
                roomUUID.set(data.room_uuid);
                // navigate to name page
                navigate("/join/name");
            }
        });
    });

    onDestroy(() => {
        ws.off("check_room_res");
    });

    const checkRoomCode = () => {
        // make sure that the code follows the pattern '000 000' with a regex
        if (code.match(/^\d{3}\s\d{3}$/)) {
            // send the code to the server
            ws.emit("check_room", { code });
        } else {
            error = "Invalid code";
        }
    };
</script>
<div>
    <p class="block is-size-2">Enter Join Code</p>
    <div class="join-input block">
        <form on:submit|preventDefault={checkRoomCode}>
            <input
                bind:value={code}
                bind:this={inp}
                class="input is-large"
                placeholder="123 456"
                maxlength="14"
                required
            />
        </form>
    </div>
    
    <div class="error-msg">{error}</div>
    
    <div class="block">
        <button on:click={checkRoomCode} class="mt-4 button is-primary is-large">
            Join Competition
        </button>
    </div>
</div>
