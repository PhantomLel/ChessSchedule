<script lang=ts>
    import { Link } from "svelte-routing";
</script>

<main class="hero is-fullheight">
  <div class="hero-head has-text-centered">
    <span class="is-size-2">Chess Tournament</span>
  </div>
  <div class="hero-body has-text-centered">
    <div class="container">
      <Link to="/join/code" class="button is-primary is-large">Join Game</Link>
      <br />
      <span class="is-size-3">- OR -</span>
      <br />
      <Link to="/create" class="button is-light is-large">Create Game</Link>
    </div>
  </div>
</main>

