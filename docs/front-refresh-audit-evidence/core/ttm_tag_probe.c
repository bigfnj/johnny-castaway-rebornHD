#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "mytypes.h"
#include "resource.h"
#include "graphics.h"
#include "ttm.h"

static unsigned char fill = 0xA5;
static struct TTtmResource resource;
void *__real_malloc(size_t size);
void *__wrap_malloc(size_t size) {
    void *p = __real_malloc(size);
    if (p) memset(p, fill, size);
    return p;
}
struct TTtmResource *findTtmResource(const char *name) {
    (void)name;
    return &resource;
}
int main(int argc, char **argv) {
    unsigned char data[] = {0x11, 0x11, 7, 0};
    struct TTtmSlot slot;
    memset(&slot, 0, sizeof(slot));
    resource.resName = "PROBE.TTM";
    resource.uncompressedData = data;
    resource.uncompressedSize = sizeof(data);
    resource.numTags = strcmp(argv[1], "valid") == 0 ? 1 : 2;
    if (strcmp(argv[1], "zero") == 0) fill = 0;
    ttmLoadTtm(&slot, resource.resName);
    if (resource.numTags == 1) {
        printf("WITNESS valid tag7=%u missing8=%u\n", ttmFindTag(&slot, 7), ttmFindTag(&slot, 8));
    } else {
        printf("WITNESS declared2 scanned1 sentinel-id=%u initialized-pattern-offset=%u\n", slot.tags[1].id, slot.tags[1].offset);
        fflush(stdout);
        printf("WITNESS sentinel lookup returned %u\n", ttmFindTag(&slot, 65535));
    }
    free(slot.tags);
    return argc == 2 ? 0 : 2;
}
