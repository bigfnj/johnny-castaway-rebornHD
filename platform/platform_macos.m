/*
 *  This file is part of 'Johnny Reborn'
 *  Platform implementation for macOS (Cocoa)
 */

#ifdef PLATFORM_MACOS

#include "platform.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <mach/mach_time.h>
#include <pthread.h>
#include <AudioToolbox/AudioToolbox.h>
#include <Cocoa/Cocoa.h>

static const char* lastError = "";
static mach_timebase_info_data_t timebaseInfo;
static uint64_t startTime;

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
    int ownPixels;  // 1 if we allocated pixels, 0 if external
};

// Window structure
@interface JCRebornWindow : NSWindow
@end

@implementation JCRebornWindow
- (BOOL)canBecomeKeyWindow { return YES; }
- (BOOL)canBecomeMainWindow { return YES; }
@end

@interface JCRebornView : NSView {
    @public
    PlatformSurface* surface;
}
@end

@implementation JCRebornView
- (void)drawRect:(NSRect)dirtyRect {
    if (!surface || !surface->pixels) return;
    
    CGContextRef context = [[NSGraphicsContext currentContext] CGContext];
    CGColorSpaceRef colorSpace = CGColorSpaceCreateDeviceRGB();
    
    // Use BGRA format to match the pixel data format (B=0, G=1, R=2, A=3)
    CGContextRef bitmapContext = CGBitmapContextCreate(
        surface->pixels,
        surface->width,
        surface->height,
        8,
        surface->pitch,
        colorSpace,
        kCGImageAlphaNoneSkipFirst | kCGBitmapByteOrder32Little
    );
    
    CGImageRef image = CGBitmapContextCreateImage(bitmapContext);
    CGRect rect = CGRectMake(0, 0, surface->width, surface->height);
    
    // Draw image directly without flipping (image data is already correct orientation)
    CGContextDrawImage(context, rect, image);
    
    CGImageRelease(image);
    CGContextRelease(bitmapContext);
    CGColorSpaceRelease(colorSpace);
}

- (BOOL)acceptsFirstResponder { return YES; }
@end

struct PlatformWindow {
    JCRebornWindow* nsWindow;
    JCRebornView* view;
    PlatformSurface* surface;
    int isFullscreen;
};

static NSMutableArray* eventQueue;
static PlatformWindow* mainWindow = NULL;

// Initialize platform
int platformInit(void) {
    @autoreleasepool {
        [NSApplication sharedApplication];
        [NSApp setActivationPolicy:NSApplicationActivationPolicyRegular];
        
        eventQueue = [[NSMutableArray alloc] init];
        
        // Initialize timing
        mach_timebase_info(&timebaseInfo);
        startTime = mach_absolute_time();
        
        return 0;
    }
}

void platformShutdown(void) {
    @autoreleasepool {
        [eventQueue release];
        [NSApp terminate:nil];
    }
}

// Window management
PlatformWindow* platformCreateWindow(const char* title, int width, int height, int fullscreen) {
    @autoreleasepool {
        PlatformWindow* window = (PlatformWindow*)malloc(sizeof(PlatformWindow));
        
        NSRect frame = NSMakeRect(0, 0, width, height);
        NSWindowStyleMask style = NSWindowStyleMaskTitled | NSWindowStyleMaskClosable | 
                                 NSWindowStyleMaskMiniaturizable;
        
        window->nsWindow = [[JCRebornWindow alloc]
            initWithContentRect:frame
            styleMask:style
            backing:NSBackingStoreBuffered
            defer:NO];
        
        [window->nsWindow setTitle:[NSString stringWithUTF8String:title]];
        [window->nsWindow center];
        [window->nsWindow makeKeyAndOrderFront:nil];
        
        window->view = [[JCRebornView alloc] initWithFrame:frame];
        [window->nsWindow setContentView:window->view];
        
        window->surface = platformCreateSurface(width, height);
        window->view->surface = window->surface;
        window->isFullscreen = 0;
        
        mainWindow = window;
        
        if (fullscreen) {
            platformToggleFullscreen(window);
        }
        
        [NSApp activateIgnoringOtherApps:YES];
        
        return window;
    }
}

void platformDestroyWindow(PlatformWindow* window) {
    @autoreleasepool {
        if (window) {
            if (window->surface) {
                platformFreeSurface(window->surface);
            }
            [window->view release];
            [window->nsWindow setReleasedWhenClosed:NO];
            [window->nsWindow close];
            [window->nsWindow release];
            free(window);
        }
    }
}

void platformShowCursor(int show) {
    @autoreleasepool {
        if (show) {
            [NSCursor unhide];
        } else {
            [NSCursor hide];
        }
    }
}

void platformToggleFullscreen(PlatformWindow* window) {
    @autoreleasepool {
        [window->nsWindow toggleFullScreen:nil];
        window->isFullscreen = !window->isFullscreen;
    }
}

void platformUpdateWindow(PlatformWindow* window) {
    @autoreleasepool {
        [window->view setNeedsDisplay:YES];
        [window->view display];
    }
}

PlatformSurface* platformGetWindowSurface(PlatformWindow* window) {
    return window->surface;
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

void platformFreeSurface(PlatformSurface* surface) {
    if (surface) {
        if (surface->ownPixels && surface->pixels) {
            free(surface->pixels);
        }
        free(surface);
    }
}

void platformLockSurface(PlatformSurface* surface) {
    (void)surface;
}

void platformUnlockSurface(PlatformSurface* surface) {
    (void)surface;
}

// Blitting and drawing

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

void platformSetColorKey(PlatformSurface* surface, uint8 r, uint8 g, uint8 b) {
    if (surface) {
        surface->hasColorKey = 1;
        surface->colorKeyR = r;
        surface->colorKeyG = g;
        surface->colorKeyB = b;
    }
}

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

void platformGetClipRect(PlatformSurface* surface, PlatformRect* rect) {
    if (surface && rect) {
        *rect = surface->clipRect;
    }
}

uint32 platformMapRGB(PlatformSurface* surface, uint8 r, uint8 g, uint8 b) {
    (void)surface;
    return (r << 16) | (g << 8) | b;
}

// Surface access
uint8* platformGetSurfacePixels(PlatformSurface* surface) {
    return surface ? surface->pixels : NULL;
}

int platformGetSurfacePitch(PlatformSurface* surface) {
    return surface ? surface->pitch : 0;
}

int platformGetSurfaceWidth(PlatformSurface* surface) {
    return surface ? surface->width : 0;
}

int platformGetSurfaceHeight(PlatformSurface* surface) {
    return surface ? surface->height : 0;
}

int platformGetSurfaceBytesPerPixel(PlatformSurface* surface) {
    return surface ? surface->bytesPerPixel : 0;
}

// Events
int platformPollEvent(PlatformEvent* event) {
    @autoreleasepool {
        NSEvent* nsEvent = [NSApp nextEventMatchingMask:NSEventMaskAny
                                              untilDate:[NSDate distantPast]
                                                 inMode:NSDefaultRunLoopMode
                                                dequeue:YES];
        
        if (!nsEvent) return 0;
        
        [NSApp sendEvent:nsEvent];
        
        event->type = EVENT_NONE;
        
        switch ([nsEvent type]) {
            case NSEventTypeKeyDown: {
                event->type = EVENT_KEY_DOWN;
                NSString* chars = [nsEvent charactersIgnoringModifiers];
                if ([chars length] > 0) {
                    unichar c = [chars characterAtIndex:0];
                    switch (c) {
                        case ' ': event->data.key.keycode = KEY_SPACE; break;
                        case '\r': case '\n': event->data.key.keycode = KEY_RETURN; break;
                        case 27: event->data.key.keycode = KEY_ESCAPE; break;
                        case 'm': case 'M': event->data.key.keycode = KEY_M; break;
                        default: event->data.key.keycode = KEY_UNKNOWN; break;
                    }
                }
                NSEventModifierFlags flags = [nsEvent modifierFlags];
                event->data.key.modifiers = 0;
                if (flags & NSEventModifierFlagOption) {
                    event->data.key.modifiers |= KEYMOD_LALT;
                }
                return 1;
            }
            
            case NSEventTypeKeyUp: {
                event->type = EVENT_KEY_UP;
                NSString *chars = [nsEvent charactersIgnoringModifiers];
                event->data.key.keycode = KEY_UNKNOWN;
                if ([chars length] > 0) {
                    unichar c = [chars characterAtIndex:0];
                    switch (c) {
                        case ' ': event->data.key.keycode = KEY_SPACE; break;
                        case '\r': case '\n': event->data.key.keycode = KEY_RETURN; break;
                        case 27: event->data.key.keycode = KEY_ESCAPE; break;
                        case 'm': case 'M': event->data.key.keycode = KEY_M; break;
                        default: break;
                    }
                }
                event->data.key.modifiers = 0;
                if ([nsEvent modifierFlags] & NSEventModifierFlagOption)
                    event->data.key.modifiers |= KEYMOD_LALT;
                return 1;
            }
            
            default:
                break;
        }
        
        return 0;
    }
}

// Timing
uint32 platformGetTicks(void) {
    uint64_t elapsed = mach_absolute_time() - startTime;
    return (uint32)((elapsed * timebaseInfo.numer) / (timebaseInfo.denom * 1000000));
}

void platformDelay(uint32 ms) {
    usleep(ms * 1000);
}

// Audio
static AudioQueueRef audioQueue = NULL;
static PlatformAudioCallback audioCallback = NULL;
static void* audioUserData = NULL;
static AudioQueueBufferRef audioBuffers[3];

static void audioOutputCallback(void* userData, AudioQueueRef queue, AudioQueueBufferRef buffer) {
    (void)userData;
    if (audioCallback) {
        audioCallback(audioUserData, (uint8*)buffer->mAudioData, buffer->mAudioDataBytesCapacity);
    } else {
        memset(buffer->mAudioData, 128, buffer->mAudioDataBytesCapacity);
    }
    AudioQueueEnqueueBuffer(queue, buffer, 0, NULL);
}

int platformInitAudio(void) {
    return 0;
}

void platformCloseAudio(void) {
    if (audioQueue) {
        AudioQueueStop(audioQueue, true);
        AudioQueueDispose(audioQueue, true);
        audioQueue = NULL;
    }
}

int platformOpenAudio(PlatformAudioSpec* spec) {
    AudioStreamBasicDescription format;
    format.mSampleRate = spec->freq;
    format.mFormatID = kAudioFormatLinearPCM;
    format.mFormatFlags = 0;  // 8-bit unsigned PCM: no flags needed (naturally packed as single bytes)
    format.mBitsPerChannel = 8;
    format.mChannelsPerFrame = spec->channels;
    format.mBytesPerFrame = spec->channels;
    format.mFramesPerPacket = 1;
    format.mBytesPerPacket = spec->channels;
    
    audioCallback = spec->callback;
    audioUserData = spec->userdata;
    
    OSStatus status = AudioQueueNewOutput(&format, audioOutputCallback, NULL,
                                         NULL, NULL, 0, &audioQueue);
    if (status != 0) {
        lastError = "Failed to create audio queue";
        return -1;
    }
    
    int bufferSize = spec->samples * spec->channels;
    for (int i = 0; i < 3; i++) {
        AudioQueueAllocateBuffer(audioQueue, bufferSize, &audioBuffers[i]);
        audioBuffers[i]->mAudioDataByteSize = bufferSize;
        audioOutputCallback(NULL, audioQueue, audioBuffers[i]);
    }
    
    return 0;
}

void platformPauseAudio(int pause) {
    if (audioQueue) {
        if (pause) {
            AudioQueuePause(audioQueue);
        } else {
            AudioQueueStart(audioQueue, NULL);
        }
    }
}

static pthread_mutex_t audioMutex = PTHREAD_MUTEX_INITIALIZER;

void platformLockAudio(void) {
    pthread_mutex_lock(&audioMutex);
}

void platformUnlockAudio(void) {
    pthread_mutex_unlock(&audioMutex);
}

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

void platformFreeWAV(uint8* audio_buf) {
    free(audio_buf);
}

const char* platformGetError(void) {
    return lastError;
}

#endif // PLATFORM_MACOS
