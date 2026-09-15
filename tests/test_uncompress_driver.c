/* Headless driver linked to the production RESOURCE decompressor. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include "uncompress.h"
#include "utils.h"

void *safe_malloc(size_t size)
{
    void *result = malloc(size);
    if (!result) fatalError("test allocation failed");
    return result;
}

JCR_NORETURN void fatalError(const char *format, ...)
{
    va_list args;
    va_start(args, format);
    vfprintf(stderr, format, args);
    va_end(args);
    fputc('\n', stderr);
    exit(1);
}

int main(int argc, char **argv)
{
    if (argc != 4) return 2;
    size_t count = strlen(argv[2]) / 2;
    if (strlen(argv[2]) != count * 2) return 2;
    uint8 *input = safe_malloc(count ? count : 1);
    for (size_t i = 0; i < count; i++) {
        unsigned value;
        if (sscanf(argv[2] + 2 * i, "%2x", &value) != 1) return 2;
        input[i] = (uint8)value;
    }
    FILE *file = tmpfile();
    if (!file || fwrite(input, 1, count, file) != count) return 2;
    free(input);
    rewind(file);
    uint32 outputSize = (uint32)strtoul(argv[3], NULL, 10);
    printf("WITNESS production uncompress method=%s input=%zu output=%u\n", argv[1], count, outputSize);
    fflush(stdout);
    uint8 *output = uncompress(file, (uint8)strtoul(argv[1], NULL, 10), (uint32)count, outputSize);
    printf("RESULT ");
    for (uint32 i = 0; i < outputSize; i++) printf("%02x", output[i]);
    printf(" consumed=%ld\n", ftell(file));
    free(output);
    fclose(file);
    return 0;
}
