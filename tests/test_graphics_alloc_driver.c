/* Real graphics.c failure paths; no display or production archive needed. */
#undef NDEBUG
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "mytypes.h"
#include "resource.h"
#include "ttm.h"
#include "graphics.h"
#include "art_style.h"

static void *failedPixels;
static int freedPixels, expectsPixels;
static uint8 packed[] = {0x12};
static uint16 width = 2, height = 1;
static struct TScrResource screen = {.resName="FAULT.SCR", .width=2, .height=1,
    .uncompressedSize=1, .uncompressedData=packed};
static struct TBmpResource sprite = {.resName="FAULT.BMP", .numImages=1,
    .widths=&width, .heights=&height, .uncompressedSize=1, .uncompressedData=packed};
struct TScrResource *findScrResource(const char *name) { (void)name; return &screen; }
struct TBmpResource *findBmpResource(const char *name) { (void)name; return &sprite; }
PlatformSurface *artStyleLoadScreen(const char *name, int w, int h)
{ (void)name; (void)w; (void)h; return NULL; }
PlatformSurface *artStyleLoadSprite(const char *name, int i, int w, int h)
{ (void)name; (void)i; (void)w; (void)h; return NULL; }
void islandRelease(void) {}
PlatformSurface *__wrap_platformCreateSurface(int w, int h)
{ assert(w > 0 && h > 0); return NULL; }
PlatformSurface *__wrap_platformCreateSurfaceFrom(void *pixels, int w, int h, int pitch)
{ assert(pixels && w > 0 && h > 0 && pitch == w * 4); failedPixels = pixels; return NULL; }
void __real_free(void *);
void __wrap_free(void *p) {
    if (p && p == failedPixels) {
        failedPixels = NULL;
        freedPixels++;
        puts("WITNESS graphics failed pixels freed"); fflush(stdout);
    }
    __real_free(p);
}
static void check_release(void) {
    assert(!expectsPixels || (failedPixels == NULL && freedPixels == 1));
}
int main(int argc, char **argv) {
    assert(argc == 2);
    printf("WITNESS graphics.c allocation %s BEGIN\n", argv[1]); fflush(stdout);
    grScale = 1;
    grHdEnabled = 0;
    expectsPixels = strcmp(argv[1], "layer") != 0;
    atexit(check_release);
    if (!strcmp(argv[1], "layer")) grNewLayer();
    else if (!strcmp(argv[1], "empty")) grInitEmptyBackground();
    else if (!strcmp(argv[1], "screen")) grLoadScreen("FAULT.SCR");
    else if (!strcmp(argv[1], "sprite")) {
        struct TTtmSlot slot = {0};
        grLoadBmp(&slot, 0, "FAULT.BMP");
    } else assert(!"unknown case");
    assert(!"required surface failure returned instead of reporting its error");
    return 1;
}
