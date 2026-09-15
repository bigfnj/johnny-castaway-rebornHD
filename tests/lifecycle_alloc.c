#include "lifecycle_alloc.h"
#undef malloc
#undef calloc
#undef realloc
#undef free
#include <stdio.h>

typedef struct { void *pointer; size_t size; } Allocation;
static Allocation live[16384];
static size_t count, bytes, total;

static void allocationError(const char *message)
{
    fprintf(stderr, "ALLOCATION TRACKER: %s\n", message);
    exit(3);
}

static void add(void *pointer, size_t size)
{
    if (!pointer) allocationError("allocation failed");
    if (count == sizeof(live) / sizeof(live[0])) allocationError("tracking capacity exceeded");
    live[count++] = (Allocation){pointer, size};
    bytes += size;
    total++;
}

static size_t find(const void *pointer)
{
    for (size_t i = 0; i < count; i++) if (live[i].pointer == pointer) return i;
    return count;
}

void *jcTestMalloc(size_t size)
{
    void *pointer = malloc(size ? size : 1);
    add(pointer, size);
    return pointer;
}

void *jcTestCalloc(size_t n, size_t size)
{
    void *pointer = calloc(n ? n : 1, size ? size : 1);
    add(pointer, n * size);
    return pointer;
}

void jcTestFree(void *pointer)
{
    if (!pointer) return;
    size_t index = find(pointer);
    if (index == count) allocationError("unknown pointer or double free");
    bytes -= live[index].size;
    live[index] = live[--count];
    free(pointer);
}

void *jcTestRealloc(void *pointer, size_t size)
{
    if (!pointer) return jcTestMalloc(size);
    if (!size) { jcTestFree(pointer); return NULL; }
    size_t index = find(pointer);
    if (index == count) allocationError("realloc of unknown pointer");
    void *result = realloc(pointer, size);
    if (!result) allocationError("reallocation failed");
    bytes = bytes - live[index].size + size;
    live[index] = (Allocation){result, size};
    return result;
}

size_t jcTestLiveBlocks(void) { return count; }
size_t jcTestLiveBytes(void) { return bytes; }
size_t jcTestTotalAllocations(void) { return total; }
int jcTestIsLive(const void *pointer) { return find(pointer) != count; }
