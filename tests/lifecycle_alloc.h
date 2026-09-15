/* Forced include for the lifecycle test target only, never production builds. */
#ifndef LIFECYCLE_ALLOC_H
#define LIFECYCLE_ALLOC_H
#include <stdlib.h>
#include <stddef.h>
void *jcTestMalloc(size_t size);
void *jcTestCalloc(size_t count, size_t size);
void *jcTestRealloc(void *pointer, size_t size);
void jcTestFree(void *pointer);
size_t jcTestLiveBlocks(void);
size_t jcTestLiveBytes(void);
size_t jcTestTotalAllocations(void);
int jcTestIsLive(const void *pointer);
#define malloc(size) jcTestMalloc(size)
#define calloc(count, size) jcTestCalloc(count, size)
#define realloc(pointer, size) jcTestRealloc(pointer, size)
#define free(pointer) jcTestFree(pointer)
#endif
