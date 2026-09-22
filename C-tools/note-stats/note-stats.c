#include <dirent.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>

#define PATH_MAX_LEN 1024
#define LINE_MAX_LEN 4096

typedef struct {
    long lines;
    long chars;
} FileStats;

typedef struct {
    long files;
    long lines;
    long chars;
} Totals;

static int has_md_suffix(const char *name)
{
    size_t len = strlen(name);
    return len > 3 && strcmp(name + len - 3, ".md") == 0;
}

static int analyze_file(const char *path, FileStats *out)
{
    FILE *fp = fopen(path, "r");
    if (fp == NULL) {
        perror(path);
        return -1;
    }

    out->lines = 0;
    out->chars = 0;

    char buf[LINE_MAX_LEN];
    while (fgets(buf, sizeof(buf), fp) != NULL) {
        out->lines++;
        for (const unsigned char *p = (const unsigned char *)buf; *p != '\0'; p++) {
            if ((*p & 0xC0) != 0x80) {
                out->chars++;
            }
        }
    }

    fclose(fp);
    return 0;
}

static int scan_dir(const char *dirpath, Totals *tot)
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
            scan_dir(path, tot);
        } else if (S_ISREG(st.st_mode) && has_md_suffix(entry->d_name)) {
            FileStats fs;
            if (analyze_file(path, &fs) == 0) {
                printf("%6ld 字  %6ld 行  %s\n", fs.chars, fs.lines, path);
                tot->files++;
                tot->lines += fs.lines;
                tot->chars += fs.chars;
            }
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

    Totals tot = {0};
    if (scan_dir(argv[1], &tot) != 0) {
        return 1;
    }

    printf("\n共 %ld 个 .md 文件，%ld 行，%ld 字\n", tot.files, tot.lines, tot.chars);
    return 0;
}
