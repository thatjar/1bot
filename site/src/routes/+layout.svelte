<script context="module">
  export const load = async ({ page }) => ({
    props: {
      key: page.path,
    },
  });
</script>

<script>
  import Nav from "../components/Nav.svelte";
  import { fly } from "svelte/transition";
  import { cubicIn, cubicOut } from "svelte/easing";

  export let data;

  const duration = 300;
  const delay = duration + 100;
  const y = 10;

  const transitionIn = { easing: cubicOut, y, duration, delay };
  const transitionOut = { easing: cubicIn, y: -y, duration };
</script>

<Nav />

{#key data.pathname}
  <main class="page" in:fly={transitionIn} out:fly={transitionOut}>
    <div class="content">
      <slot />
    </div>
  </main>
{/key}
