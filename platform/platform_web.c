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

// Audio (Web Audio API)
static PlatformAudioCallback audioCallback = NULL;
static void* audioUserData = NULL;

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
    EM_ASM({
        if (window.audioContext) {
            window.audioContext.close();
            window.audioContext = null;
        }
    });
}

/**
 * platformOpenAudio()
 *
 * Opens/configures the audio device with the requested format.
 * Parameters: spec.

 */
int platformOpenAudio(PlatformAudioSpec* spec) {
    audioCallback = spec->callback;
    audioUserData = spec->userdata;

    // Setup Web Audio via JavaScript
    EM_ASM({
        if (!window.audioContext) return;

        var bufferSize = $0;
        var sampleRate = $1;

        window.audioProcessor = window.audioContext.createScriptProcessor(bufferSize, 0, 1);
        window.audioProcessor.onaudioprocess = function(e) {
            // Audio processing would be done here
        };

        window.audioProcessor.connect(window.audioContext.destination);
    }, spec->samples, spec->freq);

    return 0;
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
