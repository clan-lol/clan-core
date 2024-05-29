export const Header = () => {
  return (
    <div class="navbar bg-base-100">
      <div class="flex-none">
        <button class="btn btn-square btn-ghost">
          <span class="material-icons">home</span>
        </button>
      </div>
      <div class="flex-1">
        <a class="btn btn-ghost text-xl">Clan</a>
      </div>
      <div class="flex-none">
        <button class="btn btn-square btn-ghost">
          <span class="material-icons">menu</span>
        </button>
      </div>
    </div>
  );
};
