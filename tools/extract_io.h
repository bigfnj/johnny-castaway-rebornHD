/* Checked, exclusive-output I/O shared by the two legacy extraction tools. */
#ifndef EXTRACT_IO_H
#define EXTRACT_IO_H
#include <stddef.h>
#include <stdio.h>

int extract_error(const char *tool, const char *path, const char *message);
FILE *extract_open_input(const char *tool, const char *path, long *size);
int extract_read(const char *tool, FILE *file, const char *path, long size,
                 long offset, unsigned char *buffer, size_t length);
FILE *extract_create(const char *tool, const char *path);
int extract_write(const char *tool, FILE **file, const char *path,
                  const void *buffer, size_t length);
unsigned int extract_u16(const unsigned char *bytes);
#endif
