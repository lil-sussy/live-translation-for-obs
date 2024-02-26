<script>
  export let translationTextMic = "fsjdflsjflsk";
  export let translationTextDiscord = "fsjdflsjflsk";
  export let translationTextMic2 = "fsjdflsjflsk";
  export let translationTextDiscord2 = "fsjdflsjflsk";

  const queryString = window.location.search;
  const urlParams = new URLSearchParams(queryString);
  const bg_color = urlParams.get('bg_color') || 'green';
  const size = urlParams.get('size') || 4;
  
  window.setInterval(function(){
    const now = new Date().toISOString();
    fetch('/api/translation/', {
      headers: {
        'Content-Type': 'application/json',
        'Request-Time': now,
      }
    }).then(response => response.json())
      .then(data => {
        if (data.mic.translated_text !== translationTextMic) {
          // translationTextMic2 = data.mic.previous_translated_text
          translationTextMic2 = data.mic.translated_text
        }
        if (data.discord.translated_text !== translationTextDiscord) {
          // translationTextDiscord2 = data.discord.previous_translated_text
          translationTextDiscord2 = data.discord.translated_text
        }
      });
    }, 1000);
</script>

<main style="--size: {size}rem; --bg-color: {bg_color}">
  <div class="translation-container translation-container-discord">
    <!-- <h2 class='translation-discord discord-smaller'><span> </span><p>{translationTextDiscord}</p></h2> -->
    <h2 class='translation-discord main-discord'><span>💬 </span><span class='discord-smaller'></span><p>{translationTextDiscord2}</p></h2>
  </div>
  <div class="translation-container">
    <!-- <h2 class='translation-mic mic-smaller'><span> </span><p>{translationTextMic}</p></h2> -->
    <h2 class='translation-mic main-mic'><span>🎤 </span><span class='mic-smaller'></span><p>{translationTextMic2}</p></h2>
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
    // background-color: var(--bg-color);
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
    text-align: center;
    height: 25%;
    box-sizing: border-box;
    padding-top: 0;
    padding-bottom: 4rem;
    p {
      margin: 0;
    }
  }
  
  .translation-container.translation-container-discord {
    height: 25%;
    padding-bottom: 4rem;
  }
  
	.translation-mic {
    position: relative;
    text-align: center;
    color: #ffff;
		font-size: var(--size);
		font-weight: 500;
    overflow: wrap;
    width: 80%;
    margin: 0;
    display: flex;
    flex-direction: row;
    justify-content: center;
    align-items: center;
    padding-bottom: 1rem;
    box-sizing: border-box;
    span {
      content: '🎤 ';
      margin-right: 1%
    }
	}
	.translation-discord {
    -webkit-text-stroke: white 2px;
    position: relative;
    box-sizing: border-box;
    margin: 0;
    text-align: center;
    display: flex;
    flex-direction: row;
    justify-content: center;
    align-items: center;
    color: #7289d9;
		font-size: calc(var(--size) * 0.6);
		font-weight: 700;
    overflow: wrap;
    width: 80%;
    padding-bottom: 1rem;
    span {
      content: '💬 ';
      margin-right: 1%;
    }
	}
  .mic-smaller {
    content: ' ';
    background: url('../spinning.gif') no-repeat center center;
    background-image: url('../spinning.gif');
    background-size: cover;
    width: 2.6rem;
    height: 2.6rem;
    span {
    }
  }
  .discord-smaller {
    content: ' ';
    background: url('../spinning.gif') no-repeat center center;
    background-image: url('../spinning.gif');
    background-size: cover;
    width: 1.7rem;
    height: 1.7rem;
    span {
    }
  }

	@media (min-width: 640px) {
		main {
			max-width: none;
		}
	}
</style>