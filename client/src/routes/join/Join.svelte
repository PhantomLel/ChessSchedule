<script lang="ts">
  import Code from "./Code.svelte";
  import { Route, Router } from "svelte-routing";
  import Name from "./Name.svelte";
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
