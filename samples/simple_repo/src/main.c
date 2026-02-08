#include <stdio.h>

#define CALL_INC(v) ((v)++)

int main(void) {
	int x = 0;
    if (x == 0) {
        goto done;
    }
    x = CALL_INC(x);

done:
    printf("%d\n", x);
    return 0;
}
