<svelte:head>
  <title>1Bot - List of Third Parties</title>
</svelte:head>

<h1>List of Third Parties</h1>
<p>
  1Bot relies on these third parties for some of its functionality. We are not
  responsible for how they handle the data you send to them.
</p>
<ul>
  <li>
    <a href="https://genius.com">Genius</a> - original source of lyrics, obtained
    via Some Random Api
  </li>
  <br />

  <li>
    <a href="https://some-random-api.com">Some Random Api</a>:<br />
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
    <a href="https://popcat.xyz/api">Pop Cat API</a>:<br />
    <b>Explicitly provided data sent with the commands:</b>
    <ul>
      <li><code>weather</code></li>
    </ul>
    <b
      >User avatar and message content (or explicitly provided text) sent with
      the commands:</b
    >
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
  <br />

  <li>
    <a href="https://translate.google.com">Google Translate</a> - for the
    <code>translate</code> command. Content of a message selected by the user (or
    explicitly provided text) sent.
  </li>
  <br />

  <li>
    <a href="https://en.wiktionary.org">Wiktionary</a> - for the
    <code>define</code> command. No data sent.
  </li>
  <br />

  <li>
    <a href="https://dictionaryapi.dev">Dictionary API</a> - for the
    <code>define</code> command. Explicitly provided text sent to the API to retrieve
    definitions from Wiktionary.
  </li>
</ul>

<div style="height: 50px;"></div>

<hr />
<h4>List last updated: 2025-04-22</h4>
