<script>
  export let translationTextMic = "Hello, World!Hello, World!Hello, World!Hello, World!Hello, World!Hello, World!Hello, World!Hello, World!";
  export let translationTextDiscord = "Hello, World!Hello, World!Hello, World!Hello, World!Hello, World!Hello, World!Hello, World!Hello, World!";
  
  window.setInterval(function(){
    fetch('/api/translation/mic/')
      .then(response => response.json())
      .then(data => {
        translationTextMic = data.raw_text;
      });
  }, 1000);
  window.setInterval(function(){
    fetch('/api/translation/discord/')
      .then(response => response.json())
      .then(data => {
        translationTextDiscord = data.translated_text;
      });
  }, 1000);
</script>

<main>
  <div class="translation-container">
    <h2 class='translation-discord'>{translationTextDiscord}</h2>
  </div>
  <div class="translation-container">
    <h2 class='translation-mic'>{translationTextMic}</h2>
  </div>
</main>

<style>
  ::global(body, html) {
    margin: 0!important;
    padding: 0!important;
  }
	main {
    display: flex;
    flex-direction: column;
    justify-content: end;
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
  
	.translation-mic {
    text-align: center;
    color: #ffff;
		font-size: 2rem;
		font-weight: 500;
    overflow: wrap;
    width: 80%;
	}
	.translation-discord {
    text-align: center;
    color: cyan;
		font-size: 1.4rem;
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