<svelte:head>
  <title>1Bot - List of Third Parties</title>
</svelte:head>

<h1>List of Third Parties</h1>
<ul>
  <li>
    <a href="https://pypi.org">PyPI</a> <br />
    <b>Data sent:</b> package name (explicitly provided by user with the
    <code>pypi</code> command)
  </li>
  <br />

  <li>
    <a href="https://www.npmjs.org">NPM</a> <br />
    <b>Data sent:</b> package name (explicitly provided by user with the
    <code>npm</code> command)
  </li>
  <br />

  <li>
    <a href="https://github.com">GitHub</a> <br />
    <b>Data sent:</b> search query (explicitly provided by user with the
    <code>github</code> command)
  </li>
  <br />

  <li><a href="https://genius.com">Genius</a> - original source of lyrics</li>
  <br />

  <li>
    <a href="https://some-random-api.com">Some Random Api</a> - obtains lyrics
    from Genius <br />
    <b>Explicitly provided data sent with the commands:</b>
    <ul>
      <li><code>lyrics</code></li>
      <li><code>megamind</code></li>
    </ul>
    <b>No data sent with the commands:</b>
    <ul>
      <li><code>dog</code></li>
      <li><code>cat</code></li>
      <li><code>panda</code></li>
    </ul>
  </li>
  <br />

  <li>
    <a href="https://popcat.xyz/api">Pop Cat API</a> <br />
    <b>Explicitly provided data sent with the commands:</b>
    <ul>
      <li><code>weather</code></li>
    </ul>
    <b>User avatar and message content sent with the commands:</b>
    <ul>
      <li><code>quote</code></li>
    </ul>
    <b>Only user avatar sent with the commands:</b>
    <ul>
      <li><code>woosh</code></li>
    </ul>
  </li>
  <br />

  <li>
    <a href="https://icanhazdadjoke.com">icanhazdadjoke</a> - for the
    <code>dadjoke</code> command. No data sent.
  </li>
  <br />

  <li>
    <a href="https://xkcd.com">xkcd</a> and
    <a href="https://explainxkcd.com">explain xkcd</a> - for the
    <code>xkcd</code> command. No data sent.
  </li>
</ul>

<div style="height: 50px;"></div>

<hr />
<h4>Last updated: 2024-12-13</h4>
