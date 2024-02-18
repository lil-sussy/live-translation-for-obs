<script>
  export let translationTextMic = "Hello, World!Hello, World!Hello, World!Hello, World!Hello, World!Hello, World!Hello, World!Hello, World!";
  export let translationTextDiscord = "Hello, World!Hello, World!Hello, World!Hello, World!Hello, World!Hello, World!Hello, World!Hello, World!";
  
  const socket = new WebSocket("ws://localhost:8001/translation-text");
  socket.onmessage = function (event) {
    console.log(event.data);
    const data = JSON.parse(event.data);
    if (data.id == 'microphone')
      translationTextMic = data.text;
    if (data.id == 'discord')
      translationTextDiscord = data.text;
  };
</script>

<main>
  <div class="translation-container">
    <h2 class='translation'>{translationTextDiscord}</h2>
  </div>
  <div class="translation-container">
    <h2 class='translation'>{translationTextMic}</h2>
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
    box-sizing: border-box;
	}
  .translation-container {
    display: flex;
    justify-content: center;
    align-items: end;
    height: 20%;
    box-sizing: border-box;
    padding-bottom: 4rem;
  }
  
	.translation {
    text-align: center;
    color: #ffff;
		font-size: 2rem;
		font-weight: 500;
    overflow: wrap;
    width: 80%;
	}

	@media (min-width: 640px) {
		main {
			max-width: none;
		}
	}
</style>