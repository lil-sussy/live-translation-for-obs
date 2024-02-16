<script>
  export let translationText = "Hello, World!";
  
  const socket = new WebSocket("ws://localhost:8001/translation-text");
  socket.onmessage = function (event) {
    const data = JSON.parse(event.data);
    console.log(data);
    translationText = data.message;
  };
</script>

<main>
  <div class="translation-container">
    <h2 class='translation'>{translationText}</h2>
  </div>
</main>

<style>
  ::global(body, html) {
    margin: 0!important;
    padding: 0!important;
  }
	main {
    background-color: black;
    width: 100vw;
    height: 100vh;
		padding: 1rem;
		max-width: 240px;
		margin: 0 auto;
	}
  .translation-container {
    display: flex;
    justify-content: center;
    align-items: end;
    height: 100%;
  }
  
	.translation {
    text-align: center;
    color: #ffff;
		font-size: 2rem;
		font-weight: 500;
	}

	@media (min-width: 640px) {
		main {
			max-width: none;
		}
	}
</style>