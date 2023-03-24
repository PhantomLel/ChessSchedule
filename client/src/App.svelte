<script lang="ts">
  import { Router, Link, Route } from 'svelte-routing'
  import HomePage from './routes/HomePage.svelte';

  export let url = "";

</script>

<Router url="{url}">
  <Route path="/" component={HomePage}></Route>
  <Route path="/join" component={HomePage}></Route>
</Router>

<style>
</style>
