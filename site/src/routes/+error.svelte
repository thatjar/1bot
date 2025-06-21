<script>
  import { page } from "$app/stores";
</script>

<h1>{$page.status}</h1>
<p>Error: {$page.error.message}</p>
<p>Go <a href="/">home</a>?</p>
