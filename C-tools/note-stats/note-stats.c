#include <dirent.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>

#define PATH_MAX_LEN 1024

static int has_md_suffix(const char *name)
{
    size_t len = strlen(name);
    return len > 3 && strcmp(name + len - 3, ".md") == 0;
}

static int scan_dir(const char *dirpath, long *count)
{
    DIR *dir = opendir(dirpath);
    if (dir == NULL) {
        perror(dirpath);
        return -1;
    }

    struct dirent *entry;
    while ((entry = readdir(dir)) != NULL) {
        if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0) {
            continue;
        }

        char path[PATH_MAX_LEN];
        int n = snprintf(path, sizeof(path), "%s/%s", dirpath, entry->d_name);
        if (n < 0 || (size_t)n >= sizeof(path)) {
            fprintf(stderr, "路径过长，跳过：%s/%s\n", dirpath, entry->d_name);
            continue;
        }

        struct stat st;
        if (stat(path, &st) != 0) {
            perror(path);
            continue;
        }

        if (S_ISDIR(st.st_mode)) {
            scan_dir(path, count);
        } else if (S_ISREG(st.st_mode) && has_md_suffix(entry->d_name)) {
            printf("%s\n", path);
            (*count)++;
        }
    }

    closedir(dir);
    return 0;
}

int main(int argc, char *argv[])
{
    if (argc < 2) {
        fprintf(stderr, "用法：note-stats <目录>\n");
        return 1;
    }

    long count = 0;
    if (scan_dir(argv[1], &count) != 0) {
        return 1;
    }

    printf("共 %ld 个 .md 文件\n", count);
    return 0;
}
