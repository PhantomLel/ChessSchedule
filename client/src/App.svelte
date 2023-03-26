<script lang="ts">
  import { Router, Link, Route } from 'svelte-routing'
  import HomePage from './routes/HomePage.svelte';
  import Create from './routes/Create.svelte';
  import Join from './routes/join/Join.svelte';

  export let url = "";

</script>

<Router url="{url}">
  <Route path="/" component={HomePage}></Route>
  <Route path="/join/*" component={Join}></Route>
  <Route path="/create" component={Create}></Route>
</Router>

<style>
</style>
