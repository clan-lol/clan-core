#define _GNU_SOURCE
#include <dlfcn.h>
#include <pwd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>

#ifdef __APPLE__
#include <sandbox.h>
#include <unistd.h>
#endif

#ifdef __APPLE__
struct dyld_interpose {
  const void *replacement;
  const void *replacee;
};
#define WRAPPER(ret, name) static ret _fakeroot_wrapper_##name
#define WRAPPER_DEF(name)                                                      \
  __attribute__((                                                              \
      used)) static struct dyld_interpose _fakeroot_interpose_##name           \
      __attribute__((section("__DATA,__interpose"))) = {                       \
          &_fakeroot_wrapper_##name, &name};
#else
#define WRAPPER(ret, name) ret name
#define WRAPPER_DEF(name)
#endif

typedef struct passwd *(*getpwnam_type)(const char *name);

WRAPPER(struct passwd *, getpwnam)(const char *name) {
  struct passwd *pw;
#ifdef __APPLE__
#define orig_getpwnam(name) getpwnam(name)
#else
  static getpwnam_type orig_getpwnam = NULL;

  if (!orig_getpwnam) {
    orig_getpwnam = (getpwnam_type)dlsym(RTLD_NEXT, "getpwnam");
    if (!orig_getpwnam) {
      fprintf(stderr, "dlsym error: %s\n", dlerror());
      exit(1);
    }
  }
#endif
  pw = orig_getpwnam(name);

  if (pw) {
    const char *shell = getenv("LOGIN_SHELL");
    if (!shell) {
      fprintf(stderr, "no LOGIN_SHELL set\n");
      exit(1);
    }
    pw->pw_shell = strdup(shell);
    fprintf(stderr, "getpwnam: %s -> %s\n", name, pw->pw_shell);
  }
  return pw;
}
WRAPPER_DEF(getpwnam)

#ifdef __APPLE__
// sandbox_init(3) doesn't work in nix build sandbox
WRAPPER(int, sandbox_init)(const char *profile, uint64_t flags, void *handle) {
  return 0;
}
WRAPPER_DEF(sandbox_init)
#else
#endif
