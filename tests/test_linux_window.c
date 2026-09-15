#include <assert.h>
#include <limits.h>
#include <stdlib.h>
#include <string.h>
#include <X11/Xlib.h>
#include <X11/Xutil.h>
static int fail_pixels, fail_image, fail_gc, fail_window, impossible_size;
static Window probe_window(Display *d, Window p, int x, int y, unsigned w,
    unsigned h, unsigned border, unsigned long line, unsigned long background) {
    return fail_window ? 0 : XCreateSimpleWindow(d, p, x, y, w, h, border, line, background);
}
/* Keep an overflow-guard mutant from requesting gigabytes on the test host. */
static void *probe_malloc(size_t n) { return fail_pixels || n > 1024 * 1024 ? NULL : malloc(n); }
static XImage *probe_image(Display *d, Visual *v, unsigned depth, int format,
    int offset, char *data, unsigned w, unsigned h, int pad, int stride) {
    return fail_image ? NULL : XCreateImage(d, v, depth, format, offset, data, w, h, pad, stride);
}
static GC probe_gc(Display *d, Drawable w, unsigned long mask, XGCValues *values) {
    return fail_gc ? NULL : XCreateGC(d, w, mask, values);
}
static int probe_attributes(Display *d, Window w, XWindowAttributes *a) {
    int result = XGetWindowAttributes(d, w, a);
    if (impossible_size) a->width = INT_MAX;
    return result;
}
#define malloc probe_malloc
#define XCreateImage probe_image
#define XCreateGC probe_gc
#define XGetWindowAttributes probe_attributes
#define XCreateSimpleWindow probe_window
#include "../platform/platform_linux.c"
#undef malloc
#undef XCreateImage
#undef XCreateGC
#undef XGetWindowAttributes
#undef XCreateSimpleWindow

static unsigned child_count(void) {
    Window root, parent, *children = NULL;
    unsigned count = 0;
    assert(XQueryTree(display, DefaultRootWindow(display), &root, &parent, &children, &count));
    if (children) XFree(children);
    return count;
}
static void check_pixels(PlatformWindow *w, int width, int height,
                         int left, int top, int drawW, int drawH) {
    XResizeWindow(display, w->window, width, height);
    XSync(display, False);
    platformUpdateWindow(w);
    XSync(display, False);
    XImage *actual = XGetImage(display, w->window, 0, 0, width, height, AllPlanes, ZPixmap);
    assert(actual);
    for (int y = 0; y < height; y++) for (int x = 0; x < width; x++) {
        unsigned long expected = 0;
        if (x >= left && x < left + drawW && y >= top && y < top + drawH) {
            int sx = (x - left) * 4 / drawW;
            int sy = (y - top) * 3 / drawH;
            expected = (unsigned long)(1 + sx + sy * 4) * 0x010305UL;
        }
        assert((XGetPixel(actual, x, y) & 0xffffffUL) == expected);
    }
    XDestroyImage(actual);
    assert(w->surface->width == 4 && w->surface->height == 3 && w->surface->pitch == 16);
    for (int i = 0; i < 12; i++) {
        uint32_t pixel;
        memcpy(&pixel, w->surface->pixels + i * 4, 4);
        assert(pixel == (uint32_t)(i + 1) * 0x010305U);
    }
}
int main(int argc, char **argv) {
    assert(argc == 2 && platformInit() == 0);
    printf("WITNESS platform_linux.c window %s BEGIN\n", argv[1]); fflush(stdout);
    unsigned initial = child_count();
    if (!strcmp(argv[1], "gc-failure") || !strcmp(argv[1], "image-failure") || !strcmp(argv[1], "window-failure")) {
        fail_gc = !strcmp(argv[1], "gc-failure");
        fail_image = !strcmp(argv[1], "image-failure");
        fail_window = !strcmp(argv[1], "window-failure");
        assert(platformCreateWindow("failure", 4, 3, 0) == NULL);
        XSync(display, False);
        assert(!mainWindow && child_count() == initial);
    } else {
        PlatformWindow *w = platformCreateWindow("pixel contract", 4, 3, 0);
        assert(w);
        for (int i = 0; i < 12; i++) {
            uint32_t pixel = (uint32_t)(i + 1) * 0x010305U;
            memcpy(w->surface->pixels + i * 4, &pixel, 4);
        }
        if (!strcmp(argv[1], "pixels")) {
            check_pixels(w, 4, 3, 0, 0, 4, 3);
            check_pixels(w, 8, 6, 0, 0, 8, 6);
            check_pixels(w, 10, 6, 1, 0, 8, 6);
            check_pixels(w, 8, 10, 0, 2, 8, 6);
            check_pixels(w, 3, 2, 0, 0, 3, 2);
            check_pixels(w, 1, 1, 0, 0, 1, 1);
            check_pixels(w, 4, 3, 0, 0, 4, 3);
        } else if (!strcmp(argv[1], "presentation-failure")) {
            check_pixels(w, 8, 6, 0, 0, 8, 6);
            XImage *previous = w->presentationImage;
            XResizeWindow(display, w->window, 10, 6);
            XSync(display, False);
            fail_pixels = 1;
            platformUpdateWindow(w);
            assert(w->presentationImage == previous && strstr(platformGetError(), "memory"));
            fail_pixels = 0; fail_image = 1;
            platformUpdateWindow(w);
            assert(w->presentationImage == previous && strstr(platformGetError(), "presentation X image"));
            fail_image = 0; impossible_size = 1;
            platformUpdateWindow(w);
            assert(w->presentationImage == previous && strstr(platformGetError(), "dimensions"));
            impossible_size = 0;
            check_pixels(w, 10, 6, 1, 0, 8, 6);
        } else if (!strcmp(argv[1], "events")) {
            XSync(display, True);
            XEvent e = {0};
            e.type = ClientMessage;
            e.xclient.data.l[0] = (long)w->wmDeleteWindow;
            XPutBackEvent(display, &e);
            e.type = KeyPress;
            e.xkey.display = display;
            e.xkey.window = w->window;
            e.xkey.keycode = XKeysymToKeycode(display, XK_m);
            XPutBackEvent(display, &e);
            e.type = ConfigureNotify;
            XPutBackEvent(display, &e);
            PlatformEvent event;
            assert(platformPollEvent(&event) && event.type == EVENT_KEY_DOWN && event.data.key.keycode == KEY_M);
            assert(platformPollEvent(&event) && event.type == EVENT_QUIT);
            assert(!platformPollEvent(&event));
        } else assert(!"unknown case");
        platformDestroyWindow(w);
        XSync(display, False);
        assert(mainWindow == NULL && child_count() == initial);
    }
    platformShutdown();
    printf("WITNESS platform_linux.c window %s PASS\n", argv[1]);
    return 0;
}
