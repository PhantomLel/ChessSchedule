<script lang="ts">
    export let pairings : {name:string, uuid:string}[][] = [];
</script>

<!-- pairings display -->
<section class="pairings box my-6 mx-2 column is-half">
    {#each  pairings as pair }
        {#if pair.length == 2}
            <div class="pair-tile">
                <span>{pair[0].name}</span>
                <span>{pair[1].name}</span>
            </div>
        {:else} 
            <div class="pair-tile">
                <span>{pair[0].name}</span>
                <span>Sitout </span>
            </div>
        {/if}
    {/each}
</section>
