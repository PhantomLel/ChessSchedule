<script lang="ts">
  import Code from "./Code.svelte";
  import { Route, Router } from "svelte-routing";
  import Name from "./Name.svelte";
  import { onDestroy, onMount } from "svelte";
  import { ws } from "../../ws";

  onMount(() => {
    ws.on("game_ended", () => {
        window.location.href = "/join/code";
    });
  });
  onDestroy(() => {
    ws.off("game_ended");
  })
</script>

<Router>
  <main class="hero is-fullheight has-text-centered">
    <div class="hero-body">
      <div class="container">
        <Route path="code" component={Code} />
        <Route path="name" component={Name} />
        <!-- 404 -->
        <Route>
          {(window.location.href = "/join/code")}
        </Route>
      </div>
    </div>
  </main>
</Router>
