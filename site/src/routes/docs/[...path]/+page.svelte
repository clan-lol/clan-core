<script lang="ts">
  let { data } = $props();
</script>

<div class="toc">
{@html data.toc}
</div>
{@html data.content}
{JSON.stringify(data.frontmatter)}

<style>
:global {

.shiki code {
  display: block;
}
.shiki .line {
  width: 100%;
  display: inline-block;
}

/* line number */
.shiki code {
  counter-reset: step;
  counter-increment: step 0;
}
.shiki .line::before {
  content: counter(step);
  counter-increment: step;
  width: 1rem;
  margin-right: 1.5rem;
  display: inline-block;
  text-align: right;
  color: rgba(115,138,148,.4);
}

/* indent guides */
.shiki .indent {
  display: inline-block;
  position: relative;
  left: var(--indent-offset);
}

.shiki .indent:empty {
  height: 1lh;
  vertical-align: bottom;
}

.shiki .indent::before {
  content: '';
  position: absolute;
  opacity: 0.15;
  width: 1px;
  height: 100%;
  background-color: currentColor;
}


/* diff */
.shiki .line.diff.remove {
  background-color: #db0a0a41;
}
.shiki .line.diff.add {
  background-color: #0adb4954;
}
.shiki .line.highlighted {
  background-color: #00000024;
}
}
</style>
