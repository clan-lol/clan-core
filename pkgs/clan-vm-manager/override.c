#include <stdio.h>
#include <stdbool.h>
#include <stdio.h>
#include <dlfcn.h>
#include <security/pam_appl.h>
#include <security/pam_modules.h>


// Overriding the weston_authenticate_user function
bool weston_authenticate_user(const char *username, const char *password) {
    printf("=====>Overridden weston_authenticate_user called with username: %s\n", username);
    return true; // Always return true
}

FILE *fopen(const char *path, const char *mode) {
    printf("==>In our own fopen, opening %s\n", path);

    FILE *(*original_fopen)(const char*, const char*);
    original_fopen = dlsym(RTLD_NEXT, "fopen");
    return (*original_fopen)(path, mode);
}


PAM_EXTERN int pam_authenticate(pam_handle_t *pamh, int flags) {
    printf("=====>Overridden pam_authenticate called\n");
    return PAM_SUCCESS; // Always return success.
}

PAM_EXTERN int pam_acct_mgmt(pam_handle_t *pamh, int flags) {
    printf("=====>Overridden pam_acct_mgmt called\n");
    return PAM_SUCCESS; // Always return success.
}
