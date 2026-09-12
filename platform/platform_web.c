/*
 *  This file is part of 'Johnny Reborn'
 *  Platform implementation for Web (Emscripten/Canvas)
 */

#ifdef PLATFORM_WEB

#include "platform.h"
#include <emscripten.h>
#include <emscripten/html5.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

static const char* lastError = "";
static double startTime;

// Surface structure
struct PlatformSurface {
    int width;
    int height;
    int pitch;
    int bytesPerPixel;
    uint8* pixels;
    uint8 hasColorKey;
    uint8 colorKeyR, colorKeyG, colorKeyB;
    PlatformRect clipRect;
    int ownPixels;
};

// Window structure
struct PlatformWindow {
    const char* canvasId;
    PlatformSurface* surface;
    int isFullscreen;
};

static PlatformWindow* mainWindow = NULL;
static PlatformEvent pendingEvents[32];
static int pendingEventCount = 0;

// Keyboard callback
EM_BOOL keyCallback(int eventType, const EmscriptenKeyboardEvent* keyEvent, void* userData) {
    if (pendingEventCount >= 32) return EM_FALSE;

    PlatformEvent* ev = &pendingEvents[pendingEventCount];
    ev->type = (eventType == EMSCRIPTEN_EVENT_KEYDOWN) ? EVENT_KEY_DOWN : EVENT_KEY_UP;
    ev->data.key.modifiers = 0;

    if (keyEvent->altKey) {
        ev->data.key.modifiers |= KEYMOD_LALT;
    }

    if (strcmp(keyEvent->key, " ") == 0 || strcmp(keyEvent->key, "Space") == 0) {
        ev->data.key.keycode = KEY_SPACE;
    } else if (strcmp(keyEvent->key, "Enter") == 0) {
        ev->data.key.keycode = KEY_RETURN;
    } else if (strcmp(keyEvent->key, "Escape") == 0) {
        ev->data.key.keycode = KEY_ESCAPE;
    } else if (strcmp(keyEvent->key, "m") == 0 || strcmp(keyEvent->key, "M") == 0) {
        ev->data.key.keycode = KEY_M;
    } else {
        ev->data.key.keycode = KEY_UNKNOWN;
    }

    pendingEventCount++;
    return EM_TRUE;
}

// Initialize platform
int platformInit(void) {
    startTime = emscripten_get_now();

    emscripten_set_keydown_callback(EMSCRIPTEN_EVENT_TARGET_WINDOW, NULL, 1, keyCallback);
    emscripten_set_keyup_callback(EMSCRIPTEN_EVENT_TARGET_WINDOW, NULL, 1, keyCallback);

    return 0;
}

/**
 * platformShutdown()
 *
 * Shuts down the platform backend and releases OS resources.
 */
void platformShutdown(void) {
    // Cleanup
}

/* Screensaver preview is a Windows concept; nothing to do here. See platform.h. */
void platformSetPreviewParent(void* parentWindowHandle) {
    UNUSED(parentWindowHandle);
}

// Window management
PlatformWindow* platformCreateWindow(const char* title, int width, int height, int fullscreen) {
    PlatformWindow* window = (PlatformWindow*)malloc(sizeof(PlatformWindow));
    window->canvasId = "#canvas";
    window->surface = platformCreateSurface(width, height);
    window->isFullscreen = 0;

    emscripten_set_canvas_element_size(window->canvasId, width, height);

    mainWindow = window;

    if (fullscreen) {
        platformToggleFullscreen(window);
    }

    return window;
}

/**
 * platformDestroyWindow()
 *
 * Destroys a window created by platformCreateWindow().
 * Parameters: window.

 */
void platformDestroyWindow(PlatformWindow* window) {
    if (window) {
        if (window->surface) {
            platformFreeSurface(window->surface);
        }
        free(window);
    }
}

/**
 * platformShowCursor()
 *
 * Shows or hides the system cursor.
 * Parameters: show.

 */
void platformShowCursor(int show) {
    if (show) {
        EM_ASM(
            document.getElementById('canvas').style.cursor = 'default';
        );
    } else {
        EM_ASM(
            document.getElementById('canvas').style.cursor = 'none';
        );
    }
}

/**
 * platformToggleFullscreen()
 *
 * Toggles fullscreen mode for the given window.
 * Parameters: window.

 */
void platformToggleFullscreen(PlatformWindow* window) {
    if (!window->isFullscreen) {
        EmscriptenFullscreenStrategy strategy = {
            .scaleMode = EMSCRIPTEN_FULLSCREEN_SCALE_DEFAULT,
            .canvasResolutionScaleMode = EMSCRIPTEN_FULLSCREEN_CANVAS_SCALE_NONE,
            .filteringMode = EMSCRIPTEN_FULLSCREEN_FILTERING_DEFAULT
        };
        emscripten_request_fullscreen_strategy(window->canvasId, 1, &strategy);
    } else {
        emscripten_exit_fullscreen();
    }
    window->isFullscreen = !window->isFullscreen;
}

/**
 * platformUpdateWindow()
 *
 * Presents the window surface to the screen (swap/paint).
 * Parameters: window.

 */
void platformUpdateWindow(PlatformWindow* window) {
    if (!window || !window->surface) return;

    // Draw pixels to canvas using JavaScript (2D context)
    EM_ASM({
        var canvas = document.querySelector('#canvas');
        if (!canvas) return;

        var ctx = canvas.getContext('2d');
        if (!ctx) return;

        var width = $0;
        var height = $1;
        var pixels = $2;

        var imageData = ctx.createImageData(width, height);
        var data = imageData.data;

        // Copy pixel data from WASM memory (BGRA -> RGBA)
        for (var i = 0; i < width * height; i++) {
            var off = i * 4;
            data[off]     = HEAPU8[pixels + off + 2]; // R <- B
            data[off + 1] = HEAPU8[pixels + off + 1]; // G
            data[off + 2] = HEAPU8[pixels + off];     // B <- R
            data[off + 3] = HEAPU8[pixels + off + 3]; // A
        }

        ctx.putImageData(imageData, 0, 0);
    }, window->surface->width, window->surface->height, window->surface->pixels);
}

/**
 * platformGetWindowSurface()
 *
 * Returns the window's primary surface for software rendering.
 * Parameters: window.

 */
PlatformSurface* platformGetWindowSurface(PlatformWindow* window) {
    return window ? window->surface : NULL;
}

// Surface management
PlatformSurface* platformCreateSurface(int width, int height) {
    PlatformSurface* surface = (PlatformSurface*)malloc(sizeof(PlatformSurface));
    surface->width = width;
    surface->height = height;
    surface->bytesPerPixel = 4;
    surface->pitch = width * 4;
    surface->pixels = (uint8*)calloc(width * height, 4);
    surface->hasColorKey = 0;
    surface->clipRect.x = 0;
    surface->clipRect.y = 0;
    surface->clipRect.w = width;
    surface->clipRect.h = height;
    surface->ownPixels = 1;
    return surface;
}

/**
 * platformCreateSurfaceFrom()
 *
 * Creates a surface from existing pixel memory (optionally taking ownership).
 * Parameters: pixels, width, height, pitch.

 */
PlatformSurface* platformCreateSurfaceFrom(void* pixels, int width, int height, int pitch) {
    PlatformSurface* surface = (PlatformSurface*)malloc(sizeof(PlatformSurface));
    surface->width = width;
    surface->height = height;
    surface->bytesPerPixel = 4;
    surface->pitch = pitch;
    surface->pixels = (uint8*)pixels;
    surface->hasColorKey = 0;
    surface->clipRect.x = 0;
    surface->clipRect.y = 0;
    surface->clipRect.w = width;
    surface->clipRect.h = height;
    surface->ownPixels = 0;
    return surface;
}

/**
 * platformFreeSurface()
 *
 * Frees a surface and any owned pixel storage.
 * Parameters: surface.

 */
void platformFreeSurface(PlatformSurface* surface) {
    if (surface) {
        if (surface->ownPixels && surface->pixels) {
            free(surface->pixels);
        }
        free(surface);
    }
}

/**
 * platformLockSurface()
 *
 * Locks a surface for direct pixel access (no-op on most backends).
 * Parameters: surface.

 */
void platformLockSurface(PlatformSurface* surface) { UNUSED(surface); }
/**
 * platformUnlockSurface()
 *
 * Unlocks a surface previously locked with platformLockSurface().
 * Parameters: surface.

 */
void platformUnlockSurface(PlatformSurface* surface) { UNUSED(surface); }

// Blitting and drawing (same as other platforms)

void platformBlitSurface(PlatformSurface* src, PlatformRect* srcRect,
                        PlatformSurface* dst, PlatformRect* dstRect) {
    if (!src || !dst || !src->pixels || !dst->pixels) return;

    int srcX = srcRect ? srcRect->x : 0;
    int srcY = srcRect ? srcRect->y : 0;
    int srcW = srcRect ? srcRect->w : src->width;
    int srcH = srcRect ? srcRect->h : src->height;

    int dstX = dstRect ? dstRect->x : 0;
    int dstY = dstRect ? dstRect->y : 0;

    // Clip to destination clip rect
    if (dstX < dst->clipRect.x) {
        srcX += dst->clipRect.x - dstX;
        srcW -= dst->clipRect.x - dstX;
        dstX = dst->clipRect.x;
    }
    if (dstY < dst->clipRect.y) {
        srcY += dst->clipRect.y - dstY;
        srcH -= dst->clipRect.y - dstY;
        dstY = dst->clipRect.y;
    }
    if (dstX + srcW > dst->clipRect.x + dst->clipRect.w) {
        srcW = dst->clipRect.x + dst->clipRect.w - dstX;
    }
    if (dstY + srcH > dst->clipRect.y + dst->clipRect.h) {
        srcH = dst->clipRect.y + dst->clipRect.h - dstY;
    }

    if (srcW <= 0 || srcH <= 0) return;

    // Software blitter with premultiplied alpha (BGRA / PBGRA).
    for (int y = 0; y < srcH; y++) {
        for (int x = 0; x < srcW; x++) {
            int sx = srcX + x;
            int sy = srcY + y;
            int dx = dstX + x;
            int dy = dstY + y;

            if (sx < 0 || sy < 0 || sx >= src->width || sy >= src->height) continue;
            if (dx < 0 || dy < 0 || dx >= dst->width || dy >= dst->height) continue;

            uint8* srcPixel = src->pixels + sy * src->pitch + sx * src->bytesPerPixel;
            uint8* dstPixel = dst->pixels + dy * dst->pitch + dx * dst->bytesPerPixel;

            // Backward-compatible color key: treat as fully transparent.
            if (src->hasColorKey) {
                if (srcPixel[0] == src->colorKeyB &&
                    srcPixel[1] == src->colorKeyG &&
                    srcPixel[2] == src->colorKeyR) {
                    continue;
                }
            }

            uint8 sa = srcPixel[3];

            // Fast paths
            if (sa == 255) {
                memcpy(dstPixel, srcPixel, 4);
                continue;
            }
            if (sa == 0) {
                continue;
            }

            uint8 inv = (uint8)(255 - sa);

            int db = dstPixel[0];
            int dg = dstPixel[1];
            int dr = dstPixel[2];
            int da = dstPixel[3];

            // premultiplied-alpha "source over"
            dstPixel[0] = (uint8)(srcPixel[0] + (db * inv + 127) / 255);
            dstPixel[1] = (uint8)(srcPixel[1] + (dg * inv + 127) / 255);
            dstPixel[2] = (uint8)(srcPixel[2] + (dr * inv + 127) / 255);
            dstPixel[3] = (uint8)(sa + (da * inv + 127) / 255);
        }
    }
}

void platformFillRect(PlatformSurface* surface, PlatformRect* rect,
                     uint8 r, uint8 g, uint8 b, uint8 a) {
    if (!surface || !surface->pixels) return;

    int x = rect ? rect->x : 0;
    int y = rect ? rect->y : 0;
    int w = rect ? rect->w : surface->width;
    int h = rect ? rect->h : surface->height;

    // Premultiply if needed (BGRA / PBGRA)
    uint8 pb = b, pg = g, pr = r;
    if (a == 0) {
        pb = pg = pr = 0;
    }
    else if (a != 255) {
        pb = (uint8)((b * a + 127) / 255);
        pg = (uint8)((g * a + 127) / 255);
        pr = (uint8)((r * a + 127) / 255);
    }

    if (x < 0) { w += x; x = 0; }
    if (y < 0) { h += y; y = 0; }
    if (w <= 0 || h <= 0) return;

    for (int py = y; py < y + h && py < surface->height; py++) {
        for (int px = x; px < x + w && px < surface->width; px++) {
            uint8* pixel = surface->pixels + py * surface->pitch + px * surface->bytesPerPixel;
            pixel[0] = pb;
            pixel[1] = pg;
            pixel[2] = pr;
            pixel[3] = a;
        }
    }
}

/**
 * platformSetColorKey()
 *
 * Enables/disables color key transparency for a surface.
 * Parameters: surface, r, g, b.

 */
void platformSetColorKey(PlatformSurface* surface, uint8 r, uint8 g, uint8 b) {
    if (surface) {
        surface->hasColorKey = 1;
        surface->colorKeyR = r;
        surface->colorKeyG = g;
        surface->colorKeyB = b;
    }
}

/**
 * platformSetClipRect()
 *
 * Sets the clipping rectangle for subsequent blits/draws.
 * Parameters: surface, rect.

 */
void platformSetClipRect(PlatformSurface* surface, PlatformRect* rect) {
    if (surface) {
        if (rect) {
            surface->clipRect = *rect;
        } else {
            surface->clipRect.x = 0;
            surface->clipRect.y = 0;
            surface->clipRect.w = surface->width;
            surface->clipRect.h = surface->height;
        }
    }
}

/**
 * platformGetClipRect()
 *
 * Gets the current clipping rectangle for a surface.
 * Parameters: surface, rect.

 */
void platformGetClipRect(PlatformSurface* surface, PlatformRect* rect) {
    if (surface && rect) {
        *rect = surface->clipRect;
    }
}

/**
 * platformMapRGB()
 *
 * Maps 8-bit RGB values to a surface-native pixel value.
 * Parameters: surface, r, g, b.

 */
uint32 platformMapRGB(PlatformSurface* surface, uint8 r, uint8 g, uint8 b) {
    return (r << 16) | (g << 8) | b;
}

/**
 * platformGetSurfacePixels()
 *
 * Returns a pointer to the surface pixel buffer.
 * Parameters: surface.

 */
uint8* platformGetSurfacePixels(PlatformSurface* surface) {
    return surface ? surface->pixels : NULL;
}

/**
 * platformGetSurfacePitch()
 *
 * Returns the number of bytes per row for the surface.
 * Parameters: surface.

 */
int platformGetSurfacePitch(PlatformSurface* surface) {
    return surface ? surface->pitch : 0;
}

/**
 * platformGetSurfaceWidth()
 *
 * Returns surface width in pixels.
 * Parameters: surface.

 */
int platformGetSurfaceWidth(PlatformSurface* surface) {
    return surface ? surface->width : 0;
}

/**
 * platformGetSurfaceHeight()
 *
 * Returns surface height in pixels.
 * Parameters: surface.

 */
int platformGetSurfaceHeight(PlatformSurface* surface) {
    return surface ? surface->height : 0;
}

/**
 * platformGetSurfaceBytesPerPixel()
 *
 * Returns bytes-per-pixel for the surface format.
 * Parameters: surface.

 */
int platformGetSurfaceBytesPerPixel(PlatformSurface* surface) {
    return surface ? surface->bytesPerPixel : 0;
}

// Events
int platformPollEvent(PlatformEvent* event) {
    if (pendingEventCount > 0) {
        *event = pendingEvents[0];
        for (int i = 1; i < pendingEventCount; i++) {
            pendingEvents[i-1] = pendingEvents[i];
        }
        pendingEventCount--;
        return 1;
    }
    return 0;
}

// Timing
uint32 platformGetTicks(void) {
    return (uint32)(emscripten_get_now() - startTime);
}

/**
 * platformDelay()
 *
 * Sleeps for the requested number of milliseconds.
 * Parameters: ms.

 */
void platformDelay(uint32 ms) {
    emscripten_sleep(ms);
}

/*  THE ONLY THING STOPPING THE TAB FROM FREEZING.
 *
 *  A zero-length asyncify sleep still unwinds the wasm stack and returns to the
 *  browser event loop, so the page repaints and stays responsive. Without an
 *  unconditional per-frame yield the engine can run arbitrarily long without
 *  ever reaching the conditional sleep in eventsWaitTick - certainly under
 *  `maxspeed`, and in practice whenever a frame's own work outlasts its delay.
 */
/* Defined with the audio code below; declared here because platformFrameYield
 * is the only caller and sits above it. */
static void webAudioPump(void);

void platformFrameYield(void) {
    /* Top up the audio queue before yielding, so the buffer the browser plays
     * while we are unwound is already scheduled. */
    webAudioPump();
    emscripten_sleep(0);
}

// Audio (Web Audio API)
static PlatformAudioCallback audioCallback = NULL;
static void* audioUserData = NULL;
static uint8* webAudioBuf = NULL;
static int webAudioFrames = 0;
static int webAudioRate = 22050;

/**
 * platformInitAudio()
 *
 * Initializes the audio subsystem for the current backend.
 */
int platformInitAudio(void) {
    // Initialize Web Audio Context via JavaScript
    EM_ASM({
        if (typeof window.audioContext === 'undefined') {
            window.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        }
    });
    return 0;
}

/**
 * platformCloseAudio()
 *
 * Closes the audio device and stops any active playback.
 */
void platformCloseAudio(void) {
    audioCallback = NULL;
    audioUserData = NULL;

    free(webAudioBuf);
    webAudioBuf = NULL;
    webAudioFrames = 0;

    EM_ASM({
        if (window.audioContext) {
            window.audioContext.close();
            window.audioContext = null;
        }
        window.jcAudioNext = 0;
    });
}

/**
 * platformOpenAudio()
 *
 * Opens/configures the audio device with the requested format.
 * Parameters: spec.

 */
int platformOpenAudio(PlatformAudioSpec* spec) {
    /*  A REAL IMPLEMENTATION, replacing a stub.
     *
     *  What was here created a ScriptProcessorNode whose onaudioprocess body was
     *  the comment "Audio processing would be done here". audioCallback was
     *  stored and never read anywhere in this file, so the engine's mixer was
     *  never once invoked: the web build was silent by construction while
     *  soundInit still decoded every WAV in the archive at startup, and README
     *  advertised Web Audio.
     *
     *  PUSH, not pull. A ScriptProcessorNode pulls from a JS callback, which
     *  would have to re-enter wasm from an event handler - awkward under
     *  ASYNCIFY, and ScriptProcessorNode is deprecated anyway. Instead the
     *  engine fills a buffer and schedules it onto the AudioContext clock, kept
     *  a fixed distance ahead of currentTime. That needs no exported symbols and
     *  no JS-to-wasm re-entry, and it self-regulates: if the frame loop stalls,
     *  the queue drains and refills rather than drifting permanently.
     */
    audioCallback = spec->callback;
    audioUserData = spec->userdata;

    webAudioRate = spec->freq;
    webAudioFrames = spec->samples > 0 ? spec->samples : 1024;

    free(webAudioBuf);
    webAudioBuf = (uint8*)malloc((size_t)webAudioFrames);
    if (!webAudioBuf) {
        lastError = "Out of memory allocating the web audio buffer";
        webAudioFrames = 0;
        return -1;
    }
    memset(webAudioBuf, 128, (size_t)webAudioFrames);   /* 128 == silence, 8-bit unsigned */

    EM_ASM({
        if (!window.audioContext) return;
        window.jcAudioNext = 0;
    });

    return 0;
}


/*  Keep roughly a quarter second of audio queued ahead of the context clock.
 *
 *  Called once per frame from platformFrameYield. The guard bounds how many
 *  buffers a single call may schedule, so a long stall cannot turn into an
 *  unbounded catch-up loop that blocks the frame it was meant to unblock.
 */
static void webAudioPump(void) {
    if (!audioCallback || !webAudioBuf || webAudioFrames <= 0)
        return;

    for (int guard = 0; guard < 8; guard++) {

        int wantMore = EM_ASM_INT({
            var ctx = window.audioContext;
            if (!ctx || ctx.state !== 'running') return 0;
            var now = ctx.currentTime;
            if (!window.jcAudioNext || window.jcAudioNext < now) {
                window.jcAudioNext = now;
            }
            return (window.jcAudioNext - now) < 0.25 ? 1 : 0;
        });

        if (!wantMore)
            return;

        audioCallback(audioUserData, webAudioBuf, webAudioFrames);

        EM_ASM({
            var ctx = window.audioContext;
            if (!ctx) return;
            /* One declaration per statement: EM_ASM is a variadic macro and the C
             * preprocessor splits on top-level commas. Braces do not protect
             * them, only parentheses do, so `var a = $0, b = $1;` becomes two
             * macro arguments and the build fails with "expected expression". */
            var ptr = $0;
            var len = $1;
            var rate = $2;

            var buf = ctx.createBuffer(1, len, rate);
            var ch = buf.getChannelData(0);
            /* 8-bit unsigned PCM, 128 is silence. */
            for (var i = 0; i < len; i++) {
                ch[i] = (HEAPU8[ptr + i] - 128) / 128.0;
            }

            var src = ctx.createBufferSource();
            src.buffer = buf;
            src.connect(ctx.destination);
            src.start(window.jcAudioNext);
            window.jcAudioNext += len / rate;
        }, webAudioBuf, webAudioFrames, webAudioRate);
    }
}

/**
 * platformPauseAudio()
 *
 * Pauses or resumes audio playback.
 * Parameters: pause.

 */
void platformPauseAudio(int pause) {
    if (pause) {
        EM_ASM({
            if (window.audioContext) {
                window.audioContext.suspend();
            }
        });
    } else {
        EM_ASM({
            if (window.audioContext) {
                window.audioContext.resume();
            }
        });
    }
}

/**
 * platformLockAudio()
 *
 * Locks the audio callback/mixing thread for safe shared access.
 */
void platformLockAudio(void) {}
/**
 * platformUnlockAudio()
 *
 * Unlocks the audio mixer lock acquired by platformLockAudio().
 */
void platformUnlockAudio(void) {}

int platformLoadWAVFromMemory(const uint8* data, uint32 dataSize,
                              PlatformAudioSpec* spec,
                              uint8** audio_buf, uint32* audio_len) {
    if (!data || dataSize < 44) return -1;
    uint32 wavDataSize = (uint32)data[40] | ((uint32)data[41] << 8) |
                         ((uint32)data[42] << 16) | ((uint32)data[43] << 24);
    if (wavDataSize > dataSize - 44) wavDataSize = dataSize - 44;
    *audio_len = wavDataSize;
    *audio_buf = (uint8*)malloc(wavDataSize);
    if (!*audio_buf) return -1;
    memcpy(*audio_buf, data + 44, wavDataSize);
    spec->freq = (int)((uint32)data[24] | ((uint32)data[25] << 8) |
                        ((uint32)data[26] << 16) | ((uint32)data[27] << 24));
    spec->channels = (uint8)data[22];
    spec->format = (uint16)data[34] | ((uint16)data[35] << 8);
    return 0;
}

/**
 * platformFreeWAV()
 *
 * Frees a WAV buffer allocated by platformLoadWAVFromMemory().
 * Parameters: audio_buf.

 */
void platformFreeWAV(uint8* audio_buf) {
    free(audio_buf);
}

/**
 * platformGetError()
 *
 * Returns a human-readable description of the last platform error.
 */
const char* platformGetError(void) {
    return lastError;
}

#endif // PLATFORM_WEB
