#include <stdio.h>
#include <stdbool.h>
#include <stdio.h>
#include <dlfcn.h>



// Overriding the weston_authenticate_user function
bool weston_authenticate_user(const char *username, const char *password) {
    printf("=====>Overridden weston_authenticate_user called with username: %s\n", username);
    return true; // Always return true
}
