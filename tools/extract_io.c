#ifndef _WIN32
#define _POSIX_C_SOURCE 200809L
#endif
#include "extract_io.h"
#include <errno.h>
#include <fcntl.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#ifdef _WIN32
#include <io.h>
#define EX_OPEN _open
#define EX_CLOSE _close
#define EX_FDOPEN _fdopen
#define EX_FLAGS (_O_WRONLY | _O_CREAT | _O_EXCL | _O_BINARY)
#define EX_MODE (_S_IREAD | _S_IWRITE)
#else
#include <unistd.h>
#define EX_OPEN open
#define EX_CLOSE close
#define EX_FDOPEN fdopen
#define EX_FLAGS (O_WRONLY | O_CREAT | O_EXCL)
#define EX_MODE 0666
#endif

int extract_error(const char *tool, const char *path, const char *message)
{
    fprintf(stderr, "FAIL %s: %s: %s\n", tool, path, message);
    return 0;
}

FILE *extract_open_input(const char *tool, const char *path, long *size)
{
    FILE *file = fopen(path, "rb");
    if (!file) { extract_error(tool, path, "cannot open input"); return NULL; }
    if (fseek(file, 0, SEEK_END) != 0 || (*size = ftell(file)) < 0) {
        extract_error(tool, path, "cannot determine input length");
        fclose(file);
        return NULL;
    }
    return file;
}

int extract_read(const char *tool, FILE *file, const char *path, long size,
                 long offset, unsigned char *buffer, size_t length)
{
    char message[160];
    if (offset < 0 || offset > size || length > (size_t)(size - offset)) {
        snprintf(message, sizeof(message), "truncated input at 0x%lX: need %lu bytes, file length %ld",
                 offset, (unsigned long)length, size);
        return extract_error(tool, path, message);
    }
    if (fseek(file, offset, SEEK_SET) != 0) {
        snprintf(message, sizeof(message), "seek failed at 0x%lX", offset);
        return extract_error(tool, path, message);
    }
    if (fread(buffer, 1, length, file) != length) {
        snprintf(message, sizeof(message), "short read at 0x%lX: expected %lu bytes", offset, (unsigned long)length);
        return extract_error(tool, path, message);
    }
    return 1;
}

FILE *extract_create(const char *tool, const char *path)
{
    int descriptor = EX_OPEN(path, EX_FLAGS, EX_MODE);
    FILE *file;
    if (descriptor < 0) {
        extract_error(tool, path, errno == EEXIST ? "output already exists (preserved)" : "cannot create output");
        return NULL;
    }
    file = EX_FDOPEN(descriptor, "wb");
    if (!file) {
        EX_CLOSE(descriptor);
        remove(path);
        extract_error(tool, path, "cannot open output stream");
    }
    return file;
}

int extract_write(const char *tool, FILE **file, const char *path,
                  const void *buffer, size_t length)
{
    int written = fwrite(buffer, 1, length, *file) == length;
    int closed = fclose(*file) == 0;
    *file = NULL;
    if (!written || !closed)
        return extract_error(tool, path, !written ? "output write failed" : "output close failed");
    return 1;
}

unsigned int extract_u16(const unsigned char *bytes)
{
    return (unsigned int)bytes[0] | ((unsigned int)bytes[1] << 8);
}
