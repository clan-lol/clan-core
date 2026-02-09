<script module lang="ts">
  export const title = "Sovereign Infrastructure by Design";
</script>

<script lang="ts">
  import config from "$config";
  import heroImage from "$lib/assets/docs-hero.jpg";
  import IconCode from "$lib/assets/icons/code.svg?component";
  import IconFlash from "$lib/assets/icons/flash.svg?component";
  import { resolve } from "$app/paths";
</script>

<header>
  <h1>{title}</h1>
  <h2>A declarative framework for reliable, self-hosted computing</h2>
</header>

<img
  class="hero"
  src={heroImage}
  width="640"
  height="360"
  alt="Documentation Hero"
/>
<p>
  Clan is a peer-to-peer framework for building and operating self-owned
  computing infrastructure. It enables individuals and teams to run their
  systems locally, collaboratively, and at scale without surrendering control to
  centralized platforms.
</p>
<div class="actions">
  <a
    class="button primary"
    href={resolve(
      `${config.docsBase}/getting-started/creating-your-first-clan`,
    )}><IconFlash width="16" />Create Clan</a
  >
  <a class="button" href="https://git.clan.lol/clan/clan-core" rel="external"
    ><IconCode width="16" />View on Gitea</a
  >
</div>

<section>
  <h2>Guides</h2>

  <dl>
    <div class="card">
      <dt>Inventory</dt>
      <dd>Learn how about inventory</dd>
    </div>
    <div class="card">
      <dt>Vars</dt>
      <dd>Learn how to use vars</dd>
    </div>
    <div class="card">
      <dt>macOS</dt>
      <dd>Using Clan to manage your macOS machines</dd>
    </div>
  </dl>
</section>

<section>
  <h2>Reference</h2>

  <dl>
    <div class="card">
      <dt>CLI</dt>
      <dd>command line interface</dd>
    </div>
    <div class="card">
      <dt>Clan Options</dt>
      <dd>Search all options</dd>
    </div>
    <div class="card">
      <dt>Services</dt>
      <dd>Discover services</dd>
    </div>
  </dl>
</section>

<style>
  header {
    margin: 80px 0 32px;
  }
  h1 {
    margin: 0;
  }
  h2 {
    margin: 0;
    font-size: inherit;
    font-weight: inherit;
    color: #415e63;
  }
  .hero {
    width: 640px;
    height: auto;
    border-radius: 24px;
    margin-left: -24px;
  }
  .actions {
    display: flex;
    justify-content: center;
    gap: 10px;
    margin: 36px 0 48px;
  }
  .button {
    display: flex;
    gap: 8px;
    border-radius: 3px;
    border: 1px solid #90b2b7;
    background: #d8e8eb;
    color: #000;
    padding: 8px 16px;
    box-shadow: inset 2px 2px 0 0 #fff;
    font-size: 16px;
    &.primary {
      color: #fff;
      border-color: #0d1416;
      background-color: #162324;
      box-shadow: inset 2px 2px 0 0 #2c4347;
    }
  }

  section {
    background: #f7f9fa;
    margin: 48px -24px;
    padding: 24px;
    border-radius: 16px;

    h2 {
      font-size: 24px;
      font-weight: 700;
      color: inherit;
    }
    dl {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
    }
    dt {
      font-size: 36px;
      padding: 24px;
    }
    dd {
      margin: 0 4px 4px 4px;
      background: url($lib/assets/purple-orange-gradient.jpg);
      background-size: cover;
      height: 95px;
      padding: 37px 23px 0;
      color: #fff;
      font-size: 14px;

      .card:first-child & {
        color: #000;
        background-image: url($lib/assets/blue-orange-gradient.jpg);
      }
    }
    .card {
      flex: 1 1 240px;
      border-radius: 6px;
      border: 1px solid #d8e8eb;
      background: #fff;
      display: flex;
      flex-direction: column;
      flex-wrap: wrap;
    }
  }
</style>
