<script lang="ts">
  import { Router, Route, navigate } from "svelte-routing";
  import HomePage from "./routes/HomePage.svelte";
  import Create from "./routes/Create.svelte";
  import Join from "./routes/join/Join.svelte";
  import Game from "./routes/game/Game.svelte";

  export let url = "";
</script>

<Router {url}>
  <Route path="/" component={HomePage} />
  <Route path="/join/*" component={Join} />
  <Route path="/game/:name/:uuid/*" let:params>
    <Game name={params.name} uuid={params.uuid} />
  </Route>
  <Route path="/create" component={Create} />
  <!-- 404 -->
  <Route>
    {(window.location.href = "/")}
  </Route>
</Router>

<style>
</style>
