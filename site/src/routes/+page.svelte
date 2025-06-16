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

<div class="header">
  <h1 style="text-align:center"><span class="grey">Why</span> Choose Us?</h1>
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
        anywhere you want, including in DMs and group chats.
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
    background-image: url("/1botbg.png");
    background-repeat: space;
    background-size: auto;
    background-attachment: fixed;
    padding: 40px 0;
    width: 100vw;
    margin-left: calc(-50vw + 50%);
    margin-top: -30px;
  }

  .intro h1 {
    margin: 15px auto;
  }

  .intro p {
    color: #ffffff;
    width: 80%;
    margin: 15px;
  }

  .intro i {
    font-size: 1.25em;
  }

  .grey {
    color: #bebebe;
  }

  #add-1bot {
    color: rgb(73, 47, 1);
    display: block;
    width: 125px;
    padding: 10px 0;
    text-decoration: none;
    font-size: 1.2em;
    background-image: linear-gradient(to top right, #ff6600, #ff8800);
    border-radius: 5px;
    box-shadow: 0 6px 11px #1c1d24;
    transition: 300ms;
  }

  #add-1bot:hover {
    color: linear-gradient(to top right, #ff8800, #ff6600);
    box-shadow: 0 5px 10px #9f8b6578;
    transform: translateY(-2px);
  }

  #add-1bot:active {
    transform: translateY(2px);
    box-shadow: none;
    color: rgb(217, 125, 45);
  }

  .features {
    justify-content: center;
    align-items: stretch;
    margin: 30px auto;
  }

  .features .card {
    display: flex;
    flex-direction: column;
    line-height: 1.5em;
    justify-content: center;
    text-align: center;
    width: 80%;
    margin: auto;
    margin-top: 10px;
    margin-bottom: 10px;
    padding: 25px 30px;
    background-color: #2d2e36;
    border-radius: 15px;
    border: 2px solid #2d2e36;
    box-shadow: 0 6px 10px #1c1d24;
  }

  .card h2 {
    margin: 10px;
    transform: translateY(30px);
    transform: translateY(-4px);
    transition: 300ms;
    font-size: 150%;
    color: rgb(217, 125, 45);
  }

  .card p {
    transition: 200ms;
    color: #ffffff;
    font-size: 120%;
  }

  .card:hover p {
    color: rgb(255, 255, 255);
    font-size: 120%;
  }

  .card:hover {
    transform: translateY(-4px);
    background-color: #23242a;
  }

  .card {
    transition: 300ms;
  }
</style>
