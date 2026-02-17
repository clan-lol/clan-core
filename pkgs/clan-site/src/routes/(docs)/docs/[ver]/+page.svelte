<script module lang="ts">
  export const title = "What is Clan?";
</script>

<script lang="ts">
  import config from "$config";
  import heroImage from "$lib/assets/docs-hero.jpg";
  import IconCode from "$lib/assets/icons/code.svg?component";
  import IconFlash from "$lib/assets/icons/flash.svg?component";
  import { resolve } from "$app/paths";
</script>

<hgroup>
  <h1>{title}</h1>
  <h2>Clan is a declarative framework for reliable, self-hosted computing</h2>
</hgroup>

<img
  class="hero"
  src={heroImage}
  width="640"
  height="360"
  alt="Documentation Hero"
/>
<div class="actions">
  <a
    class="button primary"
    href={resolve(
      `${config.docsBase}/getting-started/creating-your-first-clan`,
    )}><IconFlash width="16" />Get Started</a
  >
  <a class="button" href="https://git.clan.lol/clan/clan-core" rel="external"
    ><IconCode width="16" />View on Gitea</a
  >
</div>
<ul class="intro">
  <li>
    Declarative framework for managing fleets of machines without a central
    controller
  </li>
  <li>Peer-to-peer infrastructure management built on NixOS</li>
  <li>First-class support for networking, backups, and resource management</li>
  <li>
    Integrates with sops-nix, nixos-anywhere, and disko for provisioning and
    secrets
  </li>
  <li>
    Extensible via community-maintained Clan Services applied across multiple
    machines
  </li>
</ul>

<section>
  <h2>Guides</h2>

  <dl>
    <a href={resolve(`${config.docsBase}/guides/inventory/inventory`)}>
      <dt>Inventory</dt>
      <dd><span>Learn how about inventory</span></dd>
    </a>
    <a href={resolve(`${config.docsBase}/guides/vars/vars-overview`)}>
      <dt>Vars</dt>
      <dd><span>Learn how to use vars</span></dd>
    </a>
    <a href={resolve(`${config.docsBase}/guides/macos`)}>
      <dt>macOS</dt>
      <dd><span>Using Clan to manage your macOS machines</span></dd>
    </a>
  </dl>
</section>

<section>
  <h2>Reference</h2>
  <dl>
    <a href={resolve(`${config.docsBase}/reference/cli`)}>
      <dt>CLI</dt>
      <dd><span>command line interface</span></dd>
    </a>
    <a href={resolve(`${config.docsBase}/reference/options/clan`)}>
      <dt>Clan Options</dt>
      <dd><span>Search all options</span></dd>
    </a>
    <a href={resolve(`${config.docsBase}/services/definition`)}>
      <dt>Services</dt>
      <dd><span>Discover services</span></dd>
    </a>
  </dl>
</section>

<style>
  hgroup {
    margin: 32px 0;
  }

  h1 {
    margin: 0;
    line-height: 1.2;
  }

  h2 {
    margin: 0;
    margin-block-start: 20px;
    color: #415e63;
    font-weight: inherit;
    font-size: inherit;
  }

  .intro {
    color: #415e63;
    font-size: 16px;

    li {
      margin: 10px 0;
    }
  }

  .hero {
    inline-size: 100%;
    block-size: auto;
    border-radius: 24px;
  }

  .actions {
    display: flex;
    gap: 10px;
    justify-content: center;
    margin: 36px 0;
  }

  .button {
    display: flex;
    gap: 8px;
    padding: 8px 16px;
    color: #000;
    background: #d8e8eb;
    border: 1px solid #90b2b7;
    border-radius: 3px;
    box-shadow: inset 2px 2px 0 0 #fff;
    font-size: 16px;

    &.primary {
      color: #fff;
      background-color: #162324;
      border-color: #0d1416;
      box-shadow: inset 2px 2px 0 0 #2c4347;
    }
  }

  section {
    display: flex;
    flex-direction: column;
    padding: 0 14px;
    margin: 28px 0;
    background: var(--content-secondary-bg-color);
    border-radius: 16px;

    h2 {
      margin: 14px 0 0;
      color: inherit;
      font-weight: 700;
      font-size: 24px;
    }

    dl {
      margin: 0;

      a {
        display: flex;
        flex-flow: column;
        margin: 14px 0;
        color: inherit;
        background: var(--content-bg-color);
        border: 1px solid #d8e8eb;
        border-radius: 6px;
      }
    }

    dt {
      padding: 24px;
      font-size: 36px;
    }

    dd {
      display: flex;
      align-items: center;
      block-size: 95px;
      margin: 0 4px 4px;
      color: #fff;
      background: url($lib/assets/purple-orange-gradient.jpg);
      background-size: cover;
      font-size: 14px;

      > span {
        display: block;
        inline-size: 180px;
        margin-inline-start: 24px;
      }

      .card:first-child & {
        color: #000;
        background-image: url($lib/assets/blue-orange-gradient.jpg);
      }
    }
  }
</style>
