<script>
  import { onMount } from "svelte";
  let showMobileMenu = false;

  const handleMobileIconClick = () => {
    showMobileMenu = !showMobileMenu;
  };

  const mediaQueryHandler = (e) => {
    if (!e.matches) {
      showMobileMenu = false;
    }
  };

  onMount(() => {
    const mediaQuery = window.matchMedia("(max-width: 690px)");
    mediaQuery.addEventListener("change", mediaQueryHandler);
  });
</script>

<nav>
  <div>
    <a href="/">
      <img src="/1bot.webp" alt="Logo" height="50" />
    </a>
  </div>

  <div
    on:click={handleMobileIconClick}
    on:keydown={handleMobileIconClick}
    class={`mobile-icon${showMobileMenu ? " active" : ""}`}
    role="button"
    aria-label="Menu"
    tabindex="0"
  >
    <div class="middle-line"></div>
  </div>

  <div class={`navbar-list${showMobileMenu ? " active" : ""}`}>
    <a href="/">Home</a>
    <a href="https://top.gg/bot/884080176416309288/vote">Upvote</a>
    <a href="https://discord.gg/JGcnKxEPsW">Support Server</a>
    <a href="https://github.com/thatjar/1bot/wiki">Wiki</a>
    <a
      href="https://discord.com/oauth2/authorize?client_id=884080176416309288"
      class="add">Add 1Bot</a
    >
  </div>
</nav>
