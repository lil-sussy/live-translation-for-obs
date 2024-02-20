<script>
  export let translationTextMic = "Hello, World!Hello, World!Hello, World!Hello, World!Hello, World!Hello, World!Hello, World!Hello, World!";
  export let translationTextDiscord = "Hello, World!Hello, World!Hello, World!Hello, World!Hello, World!Hello, World!Hello, World!Hello, World!";
  export let translationTextMic2 = "Hello, World!Hello, World!Hello, World!Hello, World!Hello, World!Hello, World!Hello, World!Hello, World!";
  export let translationTextDiscord2 = "Hello, World!Hello, World!Hello, World!Hello, World!Hello, World!Hello, World!Hello, World!Hello, World!";

  const queryString = window.location.search;
  const urlParams = new URLSearchParams(queryString);
  const bg_color = urlParams.get('bg_color') || 'green';
  const size = urlParams.get('size') || 4;
  
  window.setInterval(function(){
    fetch('/api/translation/')
      .then(response => response.json())
      .then(data => {
        if (data.mic.translated_text !== translationTextMic) {
          translationTextMic2 = translationTextMic
          translationTextMic = data.mic.translated_text
        }
        if (data.discord.translated_text !== translationTextDiscord) {
          translationTextDiscord2 = translationTextDiscord
          translationTextDiscord = data.discord.translated_text
        }
      });
    }, 1000);
</script>

<main style="--size: {size}rem; --bg-color: {bg_color}">
  <div class="translation-container translation-container-discord">
    <!-- <h2 class='translation-discord'>{translationTextDiscord2}</h2> -->
    <h2 class='translation-discord'>{translationTextDiscord}</h2>
  </div>
  <div class="translation-container">
    <!-- <h2 class='translation-mic'>{translationTextMic2}</h2> -->
    <h2 class='translation-mic'>{translationTextMic}</h2>
  </div>
</main>

<style lang='scss'>
  ::global(body, html) {
    margin: 0!important;
    padding: 0!important;
  }
	main {
    display: flex;
    flex-direction: column;
    justify-content: end;
    background-color: var(--bg-color);
    width: 100vw;
    height: 100vh;
		padding: 1rem;
		max-width: 240px;
		margin: 0 auto;
    box-sizing: border-box;
	}
  .translation-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: start;
    height: 20%;
    box-sizing: border-box;
    padding-top: 0;
    padding-bottom: 4rem;
  }
  
  .translation-container.translation-container-discord {
    height: 10%;
    padding-bottom: 4rem;
  }
  
	.translation-mic {
    text-align: center;
    color: #ffff;
		font-size: var(--size);
		font-weight: 500;
    overflow: wrap;
    width: 80%;
    margin: 0;
    padding-bottom: 1rem;
	}
	.translation-discord {
    margin: 0;
    text-align: center;
    color: cyan;
		font-size: calc(var(--size) * 0.6);
		font-weight: 500;
    overflow: wrap;
    width: 80%;
    padding-bottom: 1rem;
	}

	@media (min-width: 640px) {
		main {
			max-width: none;
		}
	}
</style>