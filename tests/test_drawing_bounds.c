/* Real graphics.c drawing and ownership checks without a display or archive. */
#undef NDEBUG
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "mytypes.h"
#include "resource.h"
#include "graphics.h"
#include "art_style.h"
#include "../src/engine/dump.c"

static void *allocations[64];
static unsigned liveCount, allocCount, screenLoads, expectedAllocCount;
static int checkingOdd;
void *__real_malloc(size_t);
void *__real_calloc(size_t, size_t);
void __real_free(void *);
static void *track(void *p) {
    assert(p && liveCount < 64);
    allocations[liveCount++] = p;
    allocCount++;
    return p;
}
void *__wrap_malloc(size_t size) { return track(__real_malloc(size)); }
void *__wrap_calloc(size_t count, size_t size) { return track(__real_calloc(count, size)); }
void __wrap_free(void *p) {
    if (!p) return;
    unsigned i;
    for (i = 0; i < liveCount && allocations[i] != p; i++) {}
    assert(i < liveCount);
    allocations[i] = allocations[--liveCount];
    __real_free(p);
}

static struct TScrResource screen;
static struct TBmpResource emptyBmp = {.resName="EMPTY.BMP", .numImages=0};
static struct TPalResource palette;
struct TScrResource *findScrResource(const char *name) {
    assert(!strcmp(name, screen.resName)); return &screen;
}
struct TBmpResource *findBmpResource(const char *name) {
    assert(!strcmp(name, emptyBmp.resName)); return &emptyBmp;
}
PlatformSurface *artStyleLoadScreen(const char *name, int w, int h) {
    (void)name; (void)w; (void)h; screenLoads++; return NULL;
}
PlatformSurface *artStyleLoadSprite(const char *name, int i, int w, int h) {
    (void)name; (void)i; (void)w; (void)h; assert(!"empty BMP must not load a sprite"); return NULL;
}
void artStyleReportUsage(void) {}
void islandRelease(void) {}

static void oddCleanup(void) {
    if (checkingOdd) {
        assert(allocCount == expectedAllocCount && screenLoads == 0 && !grBackgroundSfc);
        puts("WITNESS graphics.c odd SCR refused before style/decode allocation");
        free(screen.uncompressedData);
        assert(liveCount == 0);
    }
}
static void evenScreen(void) {
    static uint8 data[] = {0x12, 0x34, 0x56, 0x78};
    screen = (struct TScrResource){.resName="EVEN.SCR", .width=4, .height=2,
        .uncompressedSize=sizeof(data), .uncompressedData=data};
    for (int scale = 1; scale <= 2; scale++) {
        grScale = scale;
        grLoadScreen(screen.resName);
        assert(platformGetSurfaceWidth(grBackgroundSfc) == 4 * scale);
        assert(platformGetSurfaceHeight(grBackgroundSfc) == 2 * scale);
        uint8 *pixels = platformGetSurfacePixels(grBackgroundSfc);
        int pitch = platformGetSurfacePitch(grBackgroundSfc);
        for (int y = 0; y < 2 * scale; y++) {
            for (int x = 0; x < 4 * scale; x++) {
                int index = (y / scale) * 4 + x / scale + 1;
                uint8 *p = pixels + y * pitch + x * 4;
                assert(p[0] == palette.colors[index].b * 4);
                assert(p[1] == palette.colors[index].g * 4);
                assert(p[2] == palette.colors[index].r * 4 && p[3] == 255);
            }
        }
        graphicsEnd();
        assert(liveCount == 0);
    }
}
static void circle(int outline) {
    PlatformSurface *surface = platformCreateSurface(640, 480);
    grDrawCircle(surface, 100, 80, 40, 40, outline ? 2 : 1, 1);
    uint8 *pixels = platformGetSurfacePixels(surface);
    int pitch = platformGetSurfacePitch(surface);
    uint8 *center = pixels + 99 * pitch + 119 * 4;
    uint8 *edge = pixels + 80 * pitch + 119 * 4;
    uint8 *outside = pixels + 79 * pitch + 99 * 4;
    assert(center[0] == 4 && center[1] == 8 && center[2] == 12 && center[3] == 255
           && "circle center pixel");
    assert(edge[0] == (outline ? 8 : 4) && edge[1] == (outline ? 16 : 8)
           && edge[2] == (outline ? 24 : 12) && edge[3] == 255 && "circle edge pixel");
    assert(outside[0] == 0 && outside[1] == 0 && outside[2] == 0 && outside[3] == 0
           && "circle outside pixel");
    grFreeLayer(surface);
}
static void circleCorpus(const char *path) {
    /* Filled/outlined, small/large, clipping/offset and both shipping scales. */
    static const int shapes[][6] = {
        {100, 80, 40, 1, 1, 0}, {100, 80, 40, 2, 1, 0},
        {-80, -160, 800, 3, 4, 0}, {630, 470, 40, 5, 6, 0},
        {150, 120, 200, 7, 8, -272}, {638, 478, 2, 9, 9, 0}
    };
    FILE *out = fopen(path, "wb");
    assert(out);
    for (int scale = 1; scale <= 2; scale++) {
        grScale = scale;
        for (unsigned i = 0; i < sizeof(shapes) / sizeof(shapes[0]); i++) {
            const int *s = shapes[i];
            PlatformSurface *surface = platformCreateSurface(640 * scale, 480 * scale);
            grDx = s[5]; grDy = 0;
            grDrawCircle(surface, s[0], s[1], s[2], s[2], (uint8)s[3], (uint8)s[4]);
            size_t bytes = (size_t)platformGetSurfacePitch(surface) * 480 * scale;
            assert(fwrite(platformGetSurfacePixels(surface), 1, bytes, out) == bytes);
            grFreeLayer(surface);
        }
    }
    assert(fclose(out) == 0);
}
int main(int argc, char **argv) {
    assert(argc >= 2);
    printf("WITNESS graphics.c drawing %s BEGIN\n", argv[1]); fflush(stdout);
    for (int i = 0; i < 16; i++) {
        palette.colors[i] = (struct TColor){(uint8)(i * 3), (uint8)(i * 2), (uint8)i};
    }
    grLoadPalette(&palette);
    grScale = 1;
    if (!strcmp(argv[1], "circle-fill")) circle(0);
    else if (!strcmp(argv[1], "circle-outline")) circle(1);
    else if (!strcmp(argv[1], "circle-corpus")) {
        assert(argc == 3); circleCorpus(argv[2]);
    } else if (!strcmp(argv[1], "even-scr")) evenScreen();
    else if (!strcmp(argv[1], "odd-scr") || !strcmp(argv[1], "odd-dump")) {
        screen = (struct TScrResource){.resName="ODD.SCR", .width=3, .height=1,
            .uncompressedSize=1, .uncompressedData=malloc(1)};
        screen.uncompressedData[0] = 0x12;
        grHdEnabled = 1;
        checkingOdd = 1;
        expectedAllocCount = allocCount;
        atexit(oddCleanup);
        if (!strcmp(argv[1], "odd-scr")) grLoadScreen(screen.resName);
        else dumpScr(&screen, &palette);
        assert(!"odd SCR was accepted");
    } else if (!strcmp(argv[1], "even-dump")) {
        static uint8 data[] = {0x12, 0x34, 0x56, 0x78};
        screen = (struct TScrResource){.resName="EVEN.SCR", .width=4, .height=2,
            .uncompressedSize=sizeof(data), .uncompressedData=data};
        dumpScr(&screen, &palette);
    } else if (!strcmp(argv[1], "empty-bmp-reload") || !strcmp(argv[1], "empty-bmp-alias")) {
        struct TTtmSlot slot = {0};
        grLoadBmp(&slot, 0, "EMPTY.BMP");
        assert(liveCount == 1 && allocCount == 1 && slot.numSprites[0] == 0);
        const char *requested = !strcmp(argv[1], "empty-bmp-alias") ? slot.bmpNames[0] : "EMPTY.BMP";
        grLoadBmp(&slot, 0, requested);
        assert(liveCount == 1 && allocCount == 2 && !strcmp(slot.bmpNames[0], "EMPTY.BMP"));
        puts("WITNESS graphics.c consecutive zero-image load retains one name");
        grReleaseBmp(&slot, 0);
    } else assert(!"unknown case");
    assert(liveCount == 0);
    printf("WITNESS graphics.c drawing %s PASS\n", argv[1]);
    return 0;
}
