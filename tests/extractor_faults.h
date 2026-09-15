/* Injected only into isolated test builds, never normal extractor binaries. */
#ifndef _WIN32
#define _POSIX_C_SOURCE 200809L
#endif
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
FILE *jcr_test_fopen(const char *, const char *);
int jcr_test_fseek(FILE *, long, int);
long jcr_test_ftell(FILE *);
size_t jcr_test_fread(void *, size_t, size_t, FILE *);
size_t jcr_test_fwrite(const void *, size_t, size_t, FILE *);
int jcr_test_fclose(FILE *);
void *jcr_test_malloc(size_t);
#define fopen jcr_test_fopen
#define fseek jcr_test_fseek
#define ftell jcr_test_ftell
#define fread jcr_test_fread
#define fwrite jcr_test_fwrite
#define fclose jcr_test_fclose
#define malloc jcr_test_malloc
