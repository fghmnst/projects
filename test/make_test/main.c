#include <stdio.h>
#include "add.h"

int main(void)
{
    int a = 3;
    int b = 5;

    int result = add(a, b);

    printf("%d + %d = %d\n", a, b, result);

    return 0;
}