/* Test-only allocator interception around the actual platform implementation. */
#undef NDEBUG /* Assertions remain executable in a Release probe. */
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#ifdef PLATFORM_WINDOWS
#include <windows.h>
static int fail_native_window, fail_native_dc;
static HWND probe_create_window(DWORD ex, LPCSTR cls, LPCSTR title, DWORD style,
    int x, int y, int w, int h, HWND parent, HMENU menu, HINSTANCE instance, LPVOID param) {
    return fail_native_window ? NULL : CreateWindowExA(ex, cls, title, style, x, y, w, h, parent, menu, instance, param);
}
static HDC probe_dc(HWND window) { return fail_native_dc ? NULL : GetDC(window); }
static BOOL probe_show(HWND window, int command) {
    /* A disabled constructor guard must fail before exposing a test window. */
    assert(!fail_native_dc && !fail_native_window);
    return ShowWindow(window, command);
}
#define CreateWindowExA probe_create_window
#define GetDC probe_dc
#define ShowWindow probe_show
#endif
static int allocation_index, fail_at, live_count;
static void *live[128];
static void *track(void *p) {
    if (p) { assert(live_count < 128); live[live_count++] = p; }
    return p;
}
static void *test_malloc(size_t size) {
    if (++allocation_index == fail_at) return NULL;
    return track(malloc(size));
}
static void *test_calloc(size_t count, size_t size) {
    if (++allocation_index == fail_at) return NULL;
    return track(calloc(count, size));
}
static void test_free(void *p) {
    if (!p) return;
    int i;
    for (i = 0; i < live_count && live[i] != p; i++) {}
    assert(i < live_count); /* Never free borrowed or already-freed pixels. */
    live[i] = live[--live_count];
    free(p);
}
#define malloc test_malloc
#define calloc test_calloc
#define free test_free
#if defined(PLATFORM_LINUX)
#include "../platform/platform_linux.c"
#elif defined(PLATFORM_WINDOWS)
#include "../platform/platform_windows.c"
#include "../platform/png_loader.c"
#elif defined(PLATFORM_WEB)
#include "../platform/platform_web.c"
#elif defined(PLATFORM_MACOS)
#include "../platform/platform_macos.m"
#endif
#undef malloc
#undef calloc
#undef free
#ifdef PLATFORM_MACOS
#include <objc/runtime.h>
static int failed_objc_allocations;
static id fail_objc_alloc(id self, SEL command, NSZone *zone) {
    (void)self; (void)command; (void)zone;
    failed_objc_allocations++;
    return nil;
}
#endif

int main(int argc, char **argv) {
    assert(argc == 2);
    printf("WITNESS platform allocation %s BEGIN\n", argv[1]); fflush(stdout);
    uint8 borrowed[24];
    memset(borrowed, 0x5a, sizeof(borrowed));
    if (!strcmp(argv[1], "native-window") || !strcmp(argv[1], "native-context")) {
#ifdef PLATFORM_WINDOWS
        fail_native_window = !strcmp(argv[1], "native-window");
        fail_native_dc = !strcmp(argv[1], "native-context");
        assert(platformCreateWindow("hidden failure", 3, 2, 0) == NULL);
#elif defined(PLATFORM_MACOS)
        /* NSApplication must exist before the hidden NSWindow allocation.
         * No launch, activation or OS-delivered input is needed for this path. */
        [NSApplication sharedApplication];
        Class cls = !strcmp(argv[1], "native-window") ? [JCRebornWindow class] : [JCRebornView class];
        SEL selector = @selector(allocWithZone:);
        const char *types = method_getTypeEncoding(class_getClassMethod(cls, selector));
        assert(class_addMethod(object_getClass(cls), selector, (IMP)fail_objc_alloc, types));
        assert(platformCreateWindow("hidden failure", 3, 2, 0) == NULL);
        assert(failed_objc_allocations == 1);
        assert(strstr(platformGetError(), !strcmp(argv[1], "native-window") ?
            "Cocoa window" : "Cocoa view"));
#else
        assert(!"native allocation case requires Windows or macOS");
#endif
    } else if (!strcmp(argv[1], "png-wrapper") || !strcmp(argv[1], "png-success")) {
#ifdef PLATFORM_WINDOWS
        static const uint8 png[] = {
            0x89,0x50,0x4e,0x47,0x0d,0x0a,0x1a,0x0a,0,0,0,0x0d,
            0x49,0x48,0x44,0x52,0,0,0,5,0,0,0,1,8,6,0,0,0,0x16,0xfe,0x64,0xf3,
            0,0,0,0x20,0x49,0x44,0x41,0x54,0x78,1,1,0x15,0,0xea,0xff,
            0,0x11,0x22,0x33,0xff,0xfa,0x64,0x32,0,0xc8,0x64,0x32,
            0x80,0xff,0,0xff,0x40,0xa8,0,0xa8,0xff,0x58,0xed,9,
            0x61,0x51,0x30,0xc4,0x9c,0,0,0,0,0x49,0x45,0x4e,0x44,0xae,0x42,0x60,0x82
        };
        fail_at = !strcmp(argv[1], "png-wrapper") ? 2 : 0;
        PlatformSurface *s = platformLoadPNGFromMemory(png, sizeof(png));
        if (fail_at) assert(!s);
        else {
            assert(s && live_count == 2);
            test_free(platformGetSurfacePixels(s));
            platformFreeSurface(s);
        }
#else
        assert(!"WIC test requires Windows");
#endif
    } else if (!strcmp(argv[1], "surface-struct")) {
        fail_at = 1;
        assert(platformCreateSurface(3, 2) == NULL);
    } else if (!strcmp(argv[1], "surface-pixels")) {
        fail_at = 2;
        assert(platformCreateSurface(3, 2) == NULL);
    } else if (!strcmp(argv[1], "borrowed-wrapper")) {
        fail_at = 1;
        assert(platformCreateSurfaceFrom(borrowed, 3, 2, 12) == NULL);
    } else if (!strncmp(argv[1], "window-", 7)) {
#ifdef PLATFORM_LINUX
        assert(platformInit() == 0);
#endif
        fail_at = atoi(argv[1] + 7);
        assert(fail_at >= 1 && fail_at <= 3);
        assert(platformCreateWindow("allocation test", 3, 2, 0) == NULL);
#ifdef PLATFORM_LINUX
        assert(mainWindow == NULL);
        platformShutdown();
#endif
    } else if (!strcmp(argv[1], "success")) {
        PlatformSurface *s = platformCreateSurface(3, 2);
        assert(s && live_count == 2);
        for (int i = 0; i < 24; i++) assert(platformGetSurfacePixels(s)[i] == 0);
        platformFreeSurface(s);
        s = platformCreateSurfaceFrom(borrowed, 3, 2, 12);
        assert(s && live_count == 1 && platformGetSurfacePixels(s) == borrowed);
        platformFreeSurface(s);
    } else assert(!"unknown case");
    assert(live_count == 0);
    for (int i = 0; i < 24; i++) assert(borrowed[i] == 0x5a);
    if (fail_at) assert(strstr(platformGetError(), "memory"));
    printf("WITNESS platform allocation %s PASS\n", argv[1]);
    return 0;
}
