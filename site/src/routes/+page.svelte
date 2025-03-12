<svelte:head>
  <title>1Bot - One bot, several uses.</title>
</svelte:head>

<div class="intro">
  <h1>
    <span class="grey">Meet</span> 1Bot.
  </h1>
  <i class="grey">One bot, several uses.</i>
  <p>
    1Bot is a fully free multipurpose Discord bot that lets you get things done
    without leaving Discord.
  </p>
  <a
    href="https://discord.com/oauth2/authorize?client_id=884080176416309288"
    id="add-1bot">Add 1Bot</a
  >
</div>

<div class="features">
  <section class="card">
    <div>
      <h2>Freedom</h2>
      <p>
        1Bot is completely free to use for everyone. There are no paywalls or
        any other kinds of restrictions. Not only free of charge, but also free
        as in freedom - it's <a href="https://github.com/thatjar/1bot"
          >open source!</a
        >
      </p>
    </div>
  </section>

  <section class="card">
    <div>
      <h2>Multipurpose</h2>
      <p>
        1Bot has a wide variety of features. Whether it is poking fun at your
        friends, managing channel permissions, or getting lyrics to a song -
        1Bot is here to help.
      </p>
    </div>
  </section>

  <section class="card">
    <div>
      <h2>Easy to use</h2>
      <p>
        Using 1Bot is a breeze. It uses Discord's latest Application Command
        features, including Slash Commands and Context Menu commands. No more
        memorising commands.
      </p>
    </div>
  </section>

  <section class="card">
    <div>
      <h2>Use Anywhere</h2>
      <p>
        1Bot now supports user installation - add it to your account and use it
        anywhere you want, including in DMs and group chats. Moderator commands
        will not be usable via user install.
      </p>
    </div>
  </section>
</div>

<style>
  .intro {
    display: flex;
    gap: 10px;
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .intro h1 {
    margin: 15px auto;
  }

  .intro i {
    font-size: 1.25em;
  }

  .grey {
    color: #d1d1d1;
  }

  #add-1bot {
    color: black;
    display: block;
    width: 125px;
    padding: 10px 0;
    text-decoration: none;
    font-size: 1.5em;
    background-image: linear-gradient(to top right, #ff6600, #ff8800);
    border-radius: 5px;

    transition: 300ms;
  }

  #add-1bot:hover {
    box-shadow: 0 5px 10px #d471007c;
    transform: translateY(-2px);
  }

  #add-1bot:active {
    transform: translateY(2px);
    box-shadow: none;
  }

  .features {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    align-items: stretch;
    margin: 30px auto;
  }

  .features .card {
    display: flex;
    flex-direction: column;
    line-height: 1.5em;
    text-align: center;
    width: 250px;
    margin: 10px;
    padding: 25px 30px;
    background-color: #2d2e36;
    border-radius: 15px;
    border: 2px solid #4c4f60;
    box-shadow: 0 6px 10px #1c1d24;
  }

  .card h2 {
    margin: 10px;
  }
</style>
