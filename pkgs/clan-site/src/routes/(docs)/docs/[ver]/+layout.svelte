<script lang="ts">
  const { children } = $props();
</script>

<div class="container">
  {@render children()}
</div>

<style>
  .container {
    /* width: 640px; */
    padding: 0 16px;
  }
</style>
