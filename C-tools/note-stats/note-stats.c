#include<stdio.h>

int main(int argc, char *argv[])
{
    if(argc < 2){
        fprintf(stderr, "用法：note-stats <目录>\n");
        return 1;
    }

    printf("目录: %s\n", argv[1]);

    return 0;
}