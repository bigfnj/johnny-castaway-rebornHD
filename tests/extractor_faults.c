#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static FILE *input;
static int requested(const char *kind) {
    const char *value = getenv("JCR_EXTRACT_FAULT");
    return value && strcmp(value, kind) == 0;
}
FILE *jcr_test_fopen(const char *path, const char *mode) {
    FILE *file = fopen(path, mode);
    if (strcmp(mode, "rb") == 0) input = file;
    return file;
}
int jcr_test_fseek(FILE *file, long offset, int origin) {
    if (requested("seek") && origin == SEEK_SET) return -1;
    return fseek(file, offset, origin);
}
long jcr_test_ftell(FILE *file) {
    return requested("tell") ? -1 : ftell(file);
}
size_t jcr_test_fread(void *buffer, size_t size, size_t count, FILE *file) {
    if (requested("read")) return 0;
    return fread(buffer, size, count, file);
}
size_t jcr_test_fwrite(const void *buffer, size_t size, size_t count, FILE *file) {
    if (requested("stdout") && file == stdout) return 0;
    if (requested("write") && file != stdout && file != stderr) return 0;
    return fwrite(buffer, size, count, file);
}
int jcr_test_fclose(FILE *file) {
    int is_input = file == input;
    int result = fclose(file);
    if (is_input) input = NULL;
    if ((is_input && requested("input-close")) || (!is_input && requested("close"))) return -1;
    return result;
}
void *jcr_test_malloc(size_t size) {
    return requested("allocate") ? NULL : malloc(size);
}
