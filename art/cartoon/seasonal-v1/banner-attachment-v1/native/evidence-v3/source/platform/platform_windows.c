/*
 *  This file is part of 'Johnny Reborn'
 *  Platform implementation for Windows (Win32)
 */

#ifdef PLATFORM_WINDOWS

#include "platform.h"
#include "jc_resources.h"
#include <windows.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

static const char* lastError = "";
static LARGE_INTEGER performanceFreq;
static LARGE_INTEGER startTime;
static CRITICAL_SECTION audioLock;
static int audioLockInitialized = 0;

static uint16 readLE16(const uint8* p) {
    return (uint16)p[0] | ((uint16)p[1] << 8);
}

static uint32 readLE32(const uint8* p) {
    return (uint32)p[0] | ((uint32)p[1] << 8) |
           ((uint32)p[2] << 16) | ((uint32)p[3] << 24);
}

// Surface structure
struct PlatformSurface {
    int width;
    int height;
    int pitch;
    int bytesPerPixel;
    uint8* pixels;
    PlatformRect clipRect;
    int ownPixels;
};

// Window structure
struct PlatformWindow {
    HWND hwnd;
    HDC hdc;
    BITMAPINFO bitmapInfo;
    PlatformSurface* surface;
    int isFullscreen;
    WINDOWPLACEMENT windowPlacement;
};

static PlatformWindow* mainWindow = NULL;
static PlatformEvent pendingEvents[32];
static int pendingEventCount = 0;

// When enabled, we use Windows Raw Input (WM_INPUT) to generate key events.
// This has an important side effect: synthesized/injected keystrokes (e.g. SendInput/PostMessage)
// do NOT generate WM_INPUT, so they won't terminate the screensaver.
static int useRawKeyboardInput = 0;

/* Parent HWND for screensaver preview mode, set via platformSetPreviewParent. */
static HWND previewParent = NULL;

void platformSetPreviewParent(void* parentWindowHandle) {
    previewParent = (HWND)parentWindowHandle;
}

static void bringWindowToForeground(HWND hwnd, int makeTopmost)
{
    if (!hwnd) return;

    // Ensure the window is visible and not minimized.
    ShowWindow(hwnd, SW_SHOWNORMAL);
    UpdateWindow(hwnd);

    // Raise in Z-order. For fullscreen/screen-saver style usage, TOPMOST helps
    // avoid the window spawning behind other apps.
    SetWindowPos(hwnd,
                 makeTopmost ? HWND_TOPMOST : HWND_NOTOPMOST,
                 0, 0, 0, 0,
                 SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW);

    BringWindowToTop(hwnd);

    // Try the straightforward activation path first.
    if (SetForegroundWindow(hwnd)) {
        SetActiveWindow(hwnd);
        SetFocus(hwnd);
        return;
    }

    // If Windows denies foreground activation (common when another window was
    // foreground moments ago), temporarily attach to the current foreground
    // thread and retry.
    {
        HWND fg = GetForegroundWindow();
        DWORD fgThread = fg ? GetWindowThreadProcessId(fg, NULL) : 0;
        DWORD curThread = GetCurrentThreadId();

        if (fgThread && fgThread != curThread) {
            AttachThreadInput(curThread, fgThread, TRUE);
            SetForegroundWindow(hwnd);
            SetActiveWindow(hwnd);
            SetFocus(hwnd);
            AttachThreadInput(curThread, fgThread, FALSE);
        }
        else {
            SetActiveWindow(hwnd);
            SetFocus(hwnd);
        }
    }

    // Fallback "raise" hack: briefly toggle TOPMOST.
    SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE);
    SetWindowPos(hwnd, makeTopmost ? HWND_TOPMOST : HWND_NOTOPMOST,
                 0, 0, 0, 0,
                 SWP_NOMOVE | SWP_NOSIZE);
}

static PlatformKeyCode mapVKeyToPlatformKey(WPARAM vkey)
{
    switch (vkey) {
        case VK_SPACE:  return KEY_SPACE;
        case VK_RETURN: return KEY_RETURN;
        case VK_ESCAPE: return KEY_ESCAPE;
        case 'M':       return KEY_M;
        case VK_MENU:
        case VK_LMENU:
            return KEY_LALT;
        default:
            return KEY_UNKNOWN;
    }
}

// Window procedure
LRESULT CALLBACK WindowProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam) {
    switch (uMsg) {
        case WM_CLOSE:
            if (pendingEventCount < 32) {
                pendingEvents[pendingEventCount].type = EVENT_QUIT;
                pendingEventCount++;
            }
            return 0;

        /*  GIVE WAY WHEN SOMETHING ELSE TAKES THE FOREGROUND.
         *
         *  WM_ACTIVATEAPP rather than WM_KILLFOCUS, because it fires when the
         *  ACTIVATION leaves this application entirely, not merely when focus
         *  moves between windows this process owns. wParam is FALSE on the way
         *  out.
         *
         *  Not gated here. The platform layer reports what happened; events.c
         *  decides what it means, and it only acts on this in screensaver mode.
         *  The /p preview is outside that gate already, because SCR_MODE_PREVIEW
         *  never sets evScreensaverMode - which matters, since a WS_CHILD
         *  preview window never holds activation and would otherwise exit the
         *  instant it appeared.
         *
         *  Coalesced like WM_MOUSEMOVE: repeated deactivations are one fact, and
         *  the 32-slot queue drops the NEWEST when full, so a burst must not be
         *  able to push out the events behind it.
         */
        case WM_ACTIVATEAPP:
            if (wParam == FALSE) {
                if (pendingEventCount > 0 &&
                    pendingEvents[pendingEventCount - 1].type == EVENT_FOCUS_LOST) {
                    /* already queued and unread; nothing to add */
                }
                else if (pendingEventCount < 32) {
                    pendingEvents[pendingEventCount].type = EVENT_FOCUS_LOST;
                    pendingEventCount++;
                }
            }
            return 0;

        case WM_INPUT:
            if (useRawKeyboardInput) {
                UINT size = 0;
                if (GetRawInputData((HRAWINPUT)lParam, RID_INPUT, NULL, &size, sizeof(RAWINPUTHEADER)) == (UINT)-1) {
                    return 0;
                }

                if (size > 0) {
                    BYTE stackBuf[128];
                    BYTE *buf = stackBuf;
                    BYTE *heapBuf = NULL;
                    if (size > sizeof(stackBuf)) {
                        heapBuf = (BYTE*)malloc(size);
                        buf = heapBuf;
                    }

                    /*  A NULL buf here is not merely "skip this event": passing
                     *  pData == NULL is the documented way to ASK GetRawInputData
                     *  for the required size, so it returns success without
                     *  writing anything - and the check below would then wave a
                     *  NULL pointer through to raw->header.dwType. The failed
                     *  allocation would defeat the very test meant to catch it. */
                    if (buf == NULL)
                        return 0;

                    if (GetRawInputData((HRAWINPUT)lParam, RID_INPUT, buf, &size, sizeof(RAWINPUTHEADER)) != (UINT)-1) {
                        RAWINPUT *raw = (RAWINPUT*)buf;
                        if (raw->header.dwType == RIM_TYPEKEYBOARD) {
                            RAWKEYBOARD *kb = &raw->data.keyboard;

                            // Some devices send VKey=255 as "fake key"; ignore it.
                            if (kb->VKey != 0xFF) {
                                int isKeyDown = ((kb->Flags & RI_KEY_BREAK) == 0);

                                if (pendingEventCount < 32) {
                                    PlatformEvent *ev = &pendingEvents[pendingEventCount];
                                    ev->type = isKeyDown ? EVENT_KEY_DOWN : EVENT_KEY_UP;
                                    ev->data.key.modifiers = 0;

                                    if (GetKeyState(VK_MENU) & 0x8000) {
                                        ev->data.key.modifiers |= KEYMOD_LALT;
                                    }

                                    ev->data.key.keycode = mapVKeyToPlatformKey(kb->VKey);
                                    pendingEventCount++;
                                }
                            }
                        }
                    }

                    if (heapBuf) {
                        free(heapBuf);
                    }
                }
            }
            return 0;

        case WM_KEYDOWN:
        case WM_SYSKEYDOWN:
            if (useRawKeyboardInput) {
                // Swallow legacy key messages so injected/simulated keys can't stop the app.
                return 0;
            }
            if (pendingEventCount < 32) {
                PlatformEvent* ev = &pendingEvents[pendingEventCount];
                ev->type = EVENT_KEY_DOWN;
                ev->data.key.modifiers = 0;

                if (GetKeyState(VK_MENU) & 0x8000) {
                    ev->data.key.modifiers |= KEYMOD_LALT;
                }

                ev->data.key.keycode = mapVKeyToPlatformKey(wParam);
                pendingEventCount++;
            }
            return 0;

        case WM_KEYUP:
        case WM_SYSKEYUP:
            if (useRawKeyboardInput) {
                // Swallow legacy key messages so injected/simulated keys can't stop the app.
                return 0;
            }
            if (pendingEventCount < 32) {
                PlatformEvent* ev = &pendingEvents[pendingEventCount];
                ev->type = EVENT_KEY_UP;
                ev->data.key.modifiers = 0;
                if (GetKeyState(VK_MENU) & 0x8000)
                    ev->data.key.modifiers |= KEYMOD_LALT;
                ev->data.key.keycode = mapVKeyToPlatformKey(wParam);
                pendingEventCount++;
            }
            return 0;

        /*  Mouse input, for screensaver exit behaviour.
         *
         *  Deliberately NOT routed through raw input, unlike the keyboard. The
         *  keyboard uses WM_INPUT specifically so that synthesized keystrokes
         *  cannot stop the app; for the mouse the opposite is wanted, because a
         *  screensaver must yield to any real pointer movement and the ordinary
         *  messages are both sufficient and simpler.
         *
         *  Position is passed through and the decision left to the caller: the
         *  shell delivers a spurious move as the fullscreen window appears under
         *  the pointer, so exiting on the first event would close the
         *  screensaver the moment it started.
         */
        case WM_MOUSEMOVE:
            /*  COALESCE, rather than append.
             *
             *  This queue holds 32 entries and drops the NEWEST when full -
             *  and by the time that check runs, PM_REMOVE has already taken the
             *  message off the OS queue, so a dropped event is lost rather than
             *  deferred. That sizing was chosen when only keys and WM_CLOSE
             *  used it. Mouse motion is a different kind of producer: it
             *  arrives in bursts of dozens, and a burst that fills the queue
             *  would discard whatever came next - including the click or the
             *  close the screensaver is supposed to exit on.
             *
             *  Only the LATEST position matters to the dead-zone test, so an
             *  unread move is overwritten in place. The queue can then never be
             *  filled by motion alone.
             */
            if (pendingEventCount > 0 &&
                pendingEvents[pendingEventCount - 1].type == EVENT_MOUSE_MOVE) {
                PlatformEvent* ev = &pendingEvents[pendingEventCount - 1];
                ev->data.mouse.x = (sint32)(short)LOWORD(lParam);
                ev->data.mouse.y = (sint32)(short)HIWORD(lParam);
            }
            else if (pendingEventCount < 32) {
                PlatformEvent* ev = &pendingEvents[pendingEventCount];
                ev->type = EVENT_MOUSE_MOVE;
                ev->data.mouse.x = (sint32)(short)LOWORD(lParam);
                ev->data.mouse.y = (sint32)(short)HIWORD(lParam);
                pendingEventCount++;
            }
            return 0;

        case WM_LBUTTONDOWN:
        case WM_RBUTTONDOWN:
        case WM_MBUTTONDOWN:
            if (pendingEventCount < 32) {
                PlatformEvent* ev = &pendingEvents[pendingEventCount];
                ev->type = EVENT_MOUSE_BUTTON_DOWN;
                ev->data.mouse.x = (sint32)(short)LOWORD(lParam);
                ev->data.mouse.y = (sint32)(short)HIWORD(lParam);
                pendingEventCount++;
            }
            return 0;

        case WM_PAINT:
            if (mainWindow) {
                platformUpdateWindow(mainWindow);
            }
            ValidateRect(hwnd, NULL);
            return 0;
    }

    return DefWindowProc(hwnd, uMsg, wParam, lParam);
}

// Initialize platform
int platformInit(void) {
    QueryPerformanceFrequency(&performanceFreq);
    QueryPerformanceCounter(&startTime);
    return 0;
}

/**
 * platformShutdown()
 *
 * Shuts down the platform backend and releases OS resources.
 */
void platformShutdown(void) {
    UnregisterClassA("JCRebornWindow", GetModuleHandle(NULL));
}

// Window management
PlatformWindow* platformCreateWindow(const char* title, int width, int height, int fullscreen) {
    WNDCLASSEXA wc = {0};
    HINSTANCE hInst = GetModuleHandle(NULL);

    /*  THE WINDOW ICON. Two things were missing and either one alone leaves the
     *  blank default box in the title bar, the taskbar and Alt-Tab.
     *
     *  First, the class never set hIcon/hIconSm, so Windows substituted its
     *  generic application icon no matter what the executable contained.
     *
     *  Second, the CMake build never compiled vs/jc_reborn/jc_reborn.rc, so the
     *  binary had no icon resource to load in the first place. The Visual Studio
     *  project did compile it, which is why the two builds disagreed. CMakeLists
     *  now enables the RC language and builds the same .rc.
     *
     *  WNDCLASSEXA rather than WNDCLASSA because the small icon is only settable
     *  through the Ex form. LoadIconA falls back to IDI_APPLICATION when the
     *  resource is absent, so a build without the .rc still gets a window rather
     *  than a failed class registration.
     */
    /*  CS_OWNDC, because the DC below is cached for the process lifetime.
     *
     *  GetDC on a class without CS_OWNDC returns a COMMON DC whose visible
     *  region is fixed at the moment it was retrieved. This code fetches one
     *  once at creation and then reuses it across the fullscreen transition,
     *  which changes the window's style, size and position. A stale visible
     *  region is the standard explanation for a window that goes blank or
     *  renders into the wrong rectangle after a mode switch.
     *
     *  CS_OWNDC gives the window its own private DC that follows those changes,
     *  which makes the existing caching correct rather than lucky. The
     *  alternative - GetDC/ReleaseDC on every present - is a per-frame cost for
     *  no benefit here, since the window is owned by this code.
     */
    wc.style         = CS_OWNDC;
    wc.cbSize        = sizeof(wc);
    wc.lpfnWndProc   = WindowProc;
    wc.hInstance     = hInst;
    wc.lpszClassName = "JCRebornWindow";
    wc.hCursor       = LoadCursor(NULL, IDC_ARROW);
    wc.hIcon         = LoadIconA(hInst, MAKEINTRESOURCEA(JC_REBORN_ICON_ID));
    wc.hIconSm       = wc.hIcon;

    if (!wc.hIcon)
        wc.hIcon = wc.hIconSm = LoadIconA(NULL, IDI_APPLICATION);

    RegisterClassExA(&wc);

    PlatformWindow* window = (PlatformWindow*)malloc(sizeof(PlatformWindow));
    if (!window) { lastError = "Out of memory allocating window"; return NULL; }
    memset(window, 0, sizeof(*window));
    window->surface = platformCreateSurface(width, height);
    if (!window->surface) { free(window); return NULL; }

    /*  PREVIEW MODE creates a CHILD of the window the shell handed us, filling
     *  it exactly, with no frame and no foreground grab. A top-level window here
     *  is the classic broken-screensaver symptom: the Settings preview pane
     *  launches something fullscreen that jumps in front of the dialog.
     *
     *  previewParent is set only by the /p path, so every other caller keeps
     *  the original behaviour exactly.
     */
    HWND parent = previewParent;

    if (parent && IsWindow(parent)) {
        RECT pr;
        if (!GetClientRect(parent, &pr)) {
            lastError = "GetClientRect failed on the preview parent window";
            goto fail;
        }

        window->hwnd = CreateWindowExA(
            0,
            "JCRebornWindow",
            title,
            WS_CHILD | WS_VISIBLE,
            0, 0,
            pr.right - pr.left,
            pr.bottom - pr.top,
            parent, NULL,
            GetModuleHandle(NULL),
            NULL
        );
    }
    else {
        DWORD style = WS_OVERLAPPEDWINDOW;
        RECT rect = {0, 0, width, height};
        AdjustWindowRect(&rect, style, FALSE);

        window->hwnd = CreateWindowExA(
            0,
            "JCRebornWindow",
            title,
            style,
            CW_USEDEFAULT, CW_USEDEFAULT,
            rect.right - rect.left,
            rect.bottom - rect.top,
            NULL, NULL,
            GetModuleHandle(NULL),
            NULL
        );
    }

    if (!window->hwnd) {
        lastError = "Failed to create window";
        goto fail;
    }

    // Prefer Raw Input keyboard events (WM_INPUT) so injected/simulated keystrokes
    // (SendInput/PostMessage/etc.) won't terminate the app.
    {
        RAWINPUTDEVICE rid;
        rid.usUsagePage = 0x01; // Generic Desktop Controls
        rid.usUsage     = 0x06; // Keyboard
        rid.dwFlags     = 0;
        rid.hwndTarget  = window->hwnd;

        useRawKeyboardInput = RegisterRawInputDevices(&rid, 1, sizeof(rid)) ? 1 : 0;
    }

    window->hdc = GetDC(window->hwnd);
    if (!window->hdc) { lastError = "Failed to get window device context"; goto fail; }
    window->isFullscreen = 0;
    window->windowPlacement.length = sizeof(WINDOWPLACEMENT);

    // Setup bitmap info
    memset(&window->bitmapInfo, 0, sizeof(BITMAPINFO));
    window->bitmapInfo.bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
    window->bitmapInfo.bmiHeader.biWidth = width;
    window->bitmapInfo.bmiHeader.biHeight = -height;  // Negative for top-down
    window->bitmapInfo.bmiHeader.biPlanes = 1;
    window->bitmapInfo.bmiHeader.biBitCount = 32;
    window->bitmapInfo.bmiHeader.biCompression = BI_RGB;

    ShowWindow(window->hwnd, SW_SHOW);
    mainWindow = window;

    if (parent && IsWindow(parent)) {
        /*  A preview must not go fullscreen and must not touch the foreground.
         *  bringWindowToForeground is deliberately aggressive - SetWindowPos
         *  HWND_TOPMOST, BringWindowToTop, SetForegroundWindow and an
         *  AttachThreadInput retry - which is right for a screensaver and
         *  precisely wrong while the user is working in the Settings dialog.
         */
        return window;
    }

    if (fullscreen) {
        platformToggleFullscreen(window);
    }

    // Make sure we start in the foreground (and, in fullscreen mode, on top).
    bringWindowToForeground(window->hwnd, fullscreen ? 1 : 0);

    return window;
fail:
    platformDestroyWindow(window);
    return NULL;
}

/**
 * platformDestroyWindow()
 *
 * Destroys a window created by platformCreateWindow().
 * Parameters: window.

 */
void platformDestroyWindow(PlatformWindow* window) {
    if (window) {
        /*  CLEAR mainWindow FIRST, before anything is freed.
         *
         *  DestroyWindow dispatches WM_DESTROY and friends synchronously, and
         *  WindowProc's WM_PAINT arm calls platformUpdateWindow(mainWindow)
         *  while ignoring its own hwnd argument. With the global still pointing
         *  here, a paint arriving during teardown reads a surface that was freed
         *  a few statements earlier.
         *
         *  Not reachable today only because every caller does
         *  graphicsEnd(); exit(255); so nothing dispatches afterwards. That is
         *  an accident of the call sites, not a property of this function.
         */
        if (mainWindow == window) {
            mainWindow = NULL;
        }
        if (window->surface) {
            platformFreeSurface(window->surface);
        }
        if (window->hdc) {
            ReleaseDC(window->hwnd, window->hdc);
        }
        if (window->hwnd) {
            DestroyWindow(window->hwnd);
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
    ShowCursor(show ? TRUE : FALSE);
}

/**
 * platformToggleFullscreen()
 *
 * Toggles fullscreen mode for the given window.
 * Parameters: window.

 */
void platformToggleFullscreen(PlatformWindow* window) {
    if (!window->isFullscreen) {
        window->windowPlacement.length = sizeof(WINDOWPLACEMENT);
        GetWindowPlacement(window->hwnd, &window->windowPlacement);

        LONG_PTR style = GetWindowLongPtr(window->hwnd, GWL_STYLE);
        style &= ~WS_OVERLAPPEDWINDOW;
        SetWindowLongPtr(window->hwnd, GWL_STYLE, style);

        MONITORINFO mi = { sizeof(mi) };
        GetMonitorInfo(MonitorFromWindow(window->hwnd, MONITOR_DEFAULTTOPRIMARY), &mi);

        SetWindowPos(window->hwnd, HWND_TOPMOST,
                    mi.rcMonitor.left, mi.rcMonitor.top,
                    mi.rcMonitor.right - mi.rcMonitor.left,
                    mi.rcMonitor.bottom - mi.rcMonitor.top,
                    SWP_NOOWNERZORDER | SWP_FRAMECHANGED);
    } else {
        LONG_PTR style = GetWindowLongPtr(window->hwnd, GWL_STYLE);
        style |= WS_OVERLAPPEDWINDOW;
        SetWindowLongPtr(window->hwnd, GWL_STYLE, style);

        SetWindowPlacement(window->hwnd, &window->windowPlacement);
        SetWindowPos(window->hwnd, HWND_NOTOPMOST, 0, 0, 0, 0,
                    SWP_NOMOVE | SWP_NOSIZE |
                    SWP_NOOWNERZORDER | SWP_FRAMECHANGED);
    }

    window->isFullscreen = !window->isFullscreen;

    // Keep the window raised after a mode switch.
    bringWindowToForeground(window->hwnd, window->isFullscreen ? 1 : 0);
}

/**
 * platformUpdateWindow()
 *
 * Presents the window surface to the screen (swap/paint).
 * Parameters: window.

 */
void platformUpdateWindow(PlatformWindow* window) {
    if (!window || !window->surface) return;

    // Get the client area size
    RECT clientRect;
    GetClientRect(window->hwnd, &clientRect);
    int clientWidth = clientRect.right - clientRect.left;
    int clientHeight = clientRect.bottom - clientRect.top;

    /*  A zero-sized client area is not an error, it is a minimised window or a
     *  degenerate rectangle, and there is nothing to present into. Without this
     *  the aspect-ratio division below is a divide by zero. It becomes reachable
     *  the moment this renders into a window it does not own, which is exactly
     *  what screensaver preview mode does.
     */
    if (clientWidth <= 0 || clientHeight <= 0) {
        return;
    }

    // Calculate aspect-ratio preserving dimensions
    float surfaceAspect = (float)window->surface->width / (float)window->surface->height;
    float windowAspect = (float)clientWidth / (float)clientHeight;

    int destWidth, destHeight, destX, destY;

    if (windowAspect > surfaceAspect) {
        // Window is wider than surface - fit to height
        destHeight = clientHeight;
        destWidth = (int)(destHeight * surfaceAspect);
        destX = (clientWidth - destWidth) / 2;
        destY = 0;
    } else {
        // Window is taller than surface - fit to width
        destWidth = clientWidth;
        destHeight = (int)(destWidth / surfaceAspect);
        destX = 0;
        destY = (clientHeight - destHeight) / 2;
    }

    // Fill borders with black if needed
    if (destX > 0 || destY > 0) {
        HBRUSH blackBrush = (HBRUSH)GetStockObject(BLACK_BRUSH);
        if (destX > 0) {
            // Left border
            RECT leftRect = {0, 0, destX, clientHeight};
            FillRect(window->hdc, &leftRect, blackBrush);
            // Right border
            RECT rightRect = {destX + destWidth, 0, clientWidth, clientHeight};
            FillRect(window->hdc, &rightRect, blackBrush);
        }
        if (destY > 0) {
            // Top border
            RECT topRect = {0, 0, clientWidth, destY};
            FillRect(window->hdc, &topRect, blackBrush);
            // Bottom border
            RECT bottomRect = {0, destY + destHeight, clientWidth, clientHeight};
            FillRect(window->hdc, &bottomRect, blackBrush);
        }
    }

    /*  HALFTONE when shrinking, which is the screensaver preview case: the
     *  engine renders at 1280x960 with HD assets and the shell's preview pane is
     *  about 152x112, and the default BLACKONWHITE stretch mode simply drops
     *  rows and columns, which looks like noise at that ratio. HALFTONE needs
     *  the brush origin reset, per the API contract.
     */
    if (destWidth < window->surface->width || destHeight < window->surface->height) {
        SetStretchBltMode(window->hdc, HALFTONE);
        SetBrushOrgEx(window->hdc, 0, 0, NULL);
    }
    else {
        SetStretchBltMode(window->hdc, COLORONCOLOR);
    }

    StretchDIBits(window->hdc,
                 destX, destY, destWidth, destHeight,
                 0, 0, window->surface->width, window->surface->height,
                 window->surface->pixels,
                 &window->bitmapInfo,
                 DIB_RGB_COLORS,
                 SRCCOPY);
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

// Surface management (same as other platforms)
PlatformSurface* platformCreateSurface(int width, int height) {
    PlatformSurface* surface = (PlatformSurface*)malloc(sizeof(PlatformSurface));
    if (!surface) { lastError = "Out of memory allocating surface"; return NULL; }
    surface->width = width;
    surface->height = height;
    surface->bytesPerPixel = 4;
    surface->pitch = width * 4;
    surface->pixels = (uint8*)calloc(width * height, 4);
    if (!surface->pixels) {
        free(surface);
        lastError = "Out of memory allocating surface pixels";
        return NULL;
    }
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
    if (!surface) { lastError = "Out of memory allocating surface wrapper"; return NULL; }
    surface->width = width;
    surface->height = height;
    surface->bytesPerPixel = 4;
    surface->pitch = pitch;
    surface->pixels = (uint8*)pixels;
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

    // Clamp to source bounds
    if (srcX < 0) { dstX -= srcX; srcW += srcX; srcX = 0; }
    if (srcY < 0) { dstY -= srcY; srcH += srcY; srcY = 0; }
    if (srcX + srcW > src->width)  srcW = src->width  - srcX;
    if (srcY + srcH > src->height) srcH = src->height - srcY;
    // Clamp to destination bounds
    if (dstX < 0) { srcX -= dstX; srcW += dstX; dstX = 0; }
    if (dstY < 0) { srcY -= dstY; srcH += dstY; dstY = 0; }
    if (dstX + srcW > dst->width)  srcW = dst->width  - dstX;
    if (dstY + srcH > dst->height) srcH = dst->height - dstY;

    if (srcW <= 0 || srcH <= 0) return;

    // Software blitter with premultiplied alpha (BGRA / PBGRA).
    for (int y = 0; y < srcH; y++) {
        uint8* srcRow = src->pixels + (srcY + y) * src->pitch + srcX * src->bytesPerPixel;
        uint8* dstRow = dst->pixels + (dstY + y) * dst->pitch + dstX * dst->bytesPerPixel;
        for (int x = 0; x < srcW; x++) {
            uint8* srcPixel = srcRow + x * src->bytesPerPixel;
            uint8* dstPixel = dstRow + x * dst->bytesPerPixel;

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

    // Clip to surface bounds
    if (x < 0) { w += x; x = 0; }
    if (y < 0) { h += y; y = 0; }
    if (x + w > surface->width)  w = surface->width  - x;
    if (y + h > surface->height) h = surface->height - y;
    if (w <= 0 || h <= 0) return;

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

    for (int py = y; py < y + h; py++) {
        for (int px = x; px < x + w; px++) {
            uint8* pixel = surface->pixels + py * surface->pitch + px * surface->bytesPerPixel;
            pixel[0] = pb;
            pixel[1] = pg;
            pixel[2] = pr;
            pixel[3] = a;
        }
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
    MSG msg;
    while (PeekMessage(&msg, NULL, 0, 0, PM_REMOVE)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }

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
    LARGE_INTEGER now;
    QueryPerformanceCounter(&now);

    uint64_t elapsed = now.QuadPart - startTime.QuadPart;
    return (uint32)((elapsed * 1000) / performanceFreq.QuadPart);
}

/**
 * platformDelay()
 *
 * Sleeps for the requested number of milliseconds.
 * Parameters: ms.

 */
void platformDelay(uint32 ms) {
    Sleep(ms);
}

/* Preemptively scheduled: nothing to yield to. See platform.h. */
void platformFrameYield(void) {
}

// Audio (using waveOut API)
static HWAVEOUT hWaveOut = NULL;
static WAVEHDR waveHeaders[2];
static uint8* audioBuffers[2];
static PlatformAudioCallback audioCallback = NULL;
static void* audioUserData = NULL;
static int audioBufferSize = 0;
static HANDLE audioEvent = NULL;
static HANDLE audioThread = NULL;
static int audioThreadRunning = 0;

/**
 * AudioThreadProc()
 *
 * Windows audio streaming thread that feeds waveOut buffers.
 * Parameters: lpParameter.

 */
DWORD WINAPI AudioThreadProc(LPVOID lpParameter) {
    UNUSED(lpParameter);
    while (audioThreadRunning) {
        WaitForSingleObject(audioEvent, INFINITE);

        if (!audioThreadRunning) break;

        // Find a buffer that's done playing
        for (int i = 0; i < 2; i++) {
            if (waveHeaders[i].dwFlags & WHDR_DONE) {
                // Fill buffer with new audio data
                EnterCriticalSection(&audioLock);
                if (audioCallback) {
                    audioCallback(audioUserData, audioBuffers[i], audioBufferSize);
                } else {
                    memset(audioBuffers[i], 128, audioBufferSize); // Silence (128 for 8-bit unsigned)
                }
                LeaveCriticalSection(&audioLock);

                // Prepare and queue the buffer
                if (waveHeaders[i].dwFlags & WHDR_PREPARED) {
                    waveOutUnprepareHeader(hWaveOut, &waveHeaders[i], sizeof(WAVEHDR));
                }
                waveHeaders[i].lpData = (LPSTR)audioBuffers[i];
                waveHeaders[i].dwBufferLength = audioBufferSize;
                waveHeaders[i].dwFlags = 0;
                waveOutPrepareHeader(hWaveOut, &waveHeaders[i], sizeof(WAVEHDR));
                waveOutWrite(hWaveOut, &waveHeaders[i], sizeof(WAVEHDR));
            }
        }
    }
    return 0;
}

void CALLBACK waveOutProc(HWAVEOUT hwo, UINT uMsg, DWORD_PTR dwInstance,
                          DWORD_PTR dwParam1, DWORD_PTR dwParam2) {
    UNUSED(hwo);
    UNUSED(dwInstance);
    UNUSED(dwParam1);
    UNUSED(dwParam2);
    if (uMsg == WOM_DONE) {
        SetEvent(audioEvent);
    }
}

/**
 * platformInitAudio()
 *
 * Initializes the audio subsystem for the current backend.
 */
int platformInitAudio(void) {
    return 0;
}

/**
 * platformCloseAudio()
 *
 * Closes the audio device and stops any active playback.
 */
void platformCloseAudio(void) {
    if (audioThreadRunning) {
        audioThreadRunning = 0;
        SetEvent(audioEvent);
        WaitForSingleObject(audioThread, INFINITE);
        CloseHandle(audioThread);
        audioThread = NULL;
    }

    if (hWaveOut) {
        waveOutReset(hWaveOut);

        for (int i = 0; i < 2; i++) {
            /*  DO NOT FREE A BUFFER THE DRIVER STILL OWNS. The MMRESULT was
             *  discarded here. waveOutPrepareHeader page-locks the buffer, and
             *  waveOutUnprepareHeader returns WAVERR_STILLPLAYING rather than
             *  unlocking it if the driver has not released it yet; freeing it
             *  anyway hands page-locked memory back to the heap, and the
             *  waveOutClose below then touches it. The failure surfaces as heap
             *  corruption at shutdown, which gets blamed on something else.
             *
             *  Joining the feeding thread above closes the race that normally
             *  makes this fire, so this is belt and braces rather than a
             *  reproduced crash - but it is one comparison.
             */
            if (waveHeaders[i].dwFlags & WHDR_PREPARED) {
                if (waveOutUnprepareHeader(hWaveOut, &waveHeaders[i],
                                           sizeof(WAVEHDR)) != MMSYSERR_NOERROR) {
                    /* Leak the buffer deliberately: a leak at process exit is
                     * strictly better than corrupting the heap on the way out. */
                    audioBuffers[i] = NULL;
                }
            }
            if (audioBuffers[i]) {
                free(audioBuffers[i]);
                audioBuffers[i] = NULL;
            }
        }

        waveOutClose(hWaveOut);
        hWaveOut = NULL;
    }

    if (audioEvent) {
        CloseHandle(audioEvent);
        audioEvent = NULL;
    }

    if (audioLockInitialized) {
        DeleteCriticalSection(&audioLock);
        audioLockInitialized = 0;
    }
}

/**
 * platformOpenAudio()
 *
 * Opens/configures the audio device with the requested format.
 * Parameters: spec.

 */
int platformOpenAudio(PlatformAudioSpec* spec) {
    WAVEFORMATEX wfx;
    wfx.wFormatTag = WAVE_FORMAT_PCM;
    wfx.nChannels = spec->channels;
    wfx.nSamplesPerSec = spec->freq;
    wfx.wBitsPerSample = 8;
    wfx.nBlockAlign = wfx.nChannels * wfx.wBitsPerSample / 8;
    wfx.nAvgBytesPerSec = wfx.nSamplesPerSec * wfx.nBlockAlign;
    wfx.cbSize = 0;

    MMRESULT result = waveOutOpen(&hWaveOut, WAVE_MAPPER, &wfx,
                                   (DWORD_PTR)waveOutProc, 0, CALLBACK_FUNCTION);
    if (result != MMSYSERR_NOERROR) {
        lastError = "Failed to open audio device";
        return -1;
    }

    audioCallback = spec->callback;
    audioUserData = spec->userdata;
    audioBufferSize = spec->samples * spec->channels;

    // Initialize audio lock
    if (!audioLockInitialized) {
        InitializeCriticalSection(&audioLock);
        audioLockInitialized = 1;
    }

    /*  EVERY FAILURE BELOW TEARS DOWN. This function used to allocate the
     *  buffers, prepare them, queue them and only then create the thread, and if
     *  CreateThread failed it returned -1 leaving the device open with two
     *  page-locked buffers permanently queued, an event handle and an
     *  initialised CRITICAL_SECTION. Nothing ever reclaimed them, because
     *  soundInit sets soundDisabled on failure (sound.c:138-142) and soundEnd
     *  early-returns on soundDisabled (sound.c:151-152), so platformCloseAudio
     *  was never reached. All of it survived to process exit.
     *
     *  platformCloseAudio null-checks every member, so it is safe to call
     *  against the partial state built up here and is reused rather than
     *  duplicated.
     */

    // Create audio event
    audioEvent = CreateEvent(NULL, FALSE, FALSE, NULL);
    if (!audioEvent) {
        /*  Unchecked before, and the consequence was invisible rather than
         *  loud: AudioThreadProc waits on this handle, so a NULL event makes
         *  WaitForSingleObject return WAIT_FAILED immediately and the thread
         *  spins at 100% CPU forever, with no audio and nothing logged. A
         *  broken run looked exactly like a working one.
         */
        lastError = "CreateEvent failed for the audio thread";
        platformCloseAudio();
        return -1;
    }

    // Allocate and prepare buffers
    for (int i = 0; i < 2; i++) {
        audioBuffers[i] = (uint8*)malloc(audioBufferSize);
        if (!audioBuffers[i]) {
            /* The memset below dereferenced this without checking. */
            lastError = "Out of memory allocating an audio buffer";
            platformCloseAudio();
            return -1;
        }
        memset(audioBuffers[i], 128, audioBufferSize); // Silence

        memset(&waveHeaders[i], 0, sizeof(WAVEHDR));
        waveHeaders[i].lpData = (LPSTR)audioBuffers[i];
        waveHeaders[i].dwBufferLength = audioBufferSize;
        waveHeaders[i].dwFlags = 0;

        if (waveOutPrepareHeader(hWaveOut, &waveHeaders[i], sizeof(WAVEHDR)) != MMSYSERR_NOERROR) {
            lastError = "waveOutPrepareHeader failed";
            platformCloseAudio();
            return -1;
        }
        if (waveOutWrite(hWaveOut, &waveHeaders[i], sizeof(WAVEHDR)) != MMSYSERR_NOERROR) {
            lastError = "waveOutWrite failed queueing the initial buffer";
            platformCloseAudio();
            return -1;
        }
    }

    // Start audio thread
    audioThreadRunning = 1;
    audioThread = CreateThread(NULL, 0, AudioThreadProc, NULL, 0, NULL);
    if (!audioThread) {
        lastError = "CreateThread failed for the audio thread";
        audioThreadRunning = 0;
        platformCloseAudio();
        return -1;
    }

    return 0;
}

/**
 * platformPauseAudio()
 *
 * Pauses or resumes audio playback.
 * Parameters: pause.

 */
void platformPauseAudio(int pause) {
    if (hWaveOut) {
        if (pause) {
            waveOutPause(hWaveOut);
        } else {
            waveOutRestart(hWaveOut);
        }
    }
}

/**
 * platformLockAudio()
 *
 * Locks the audio callback/mixing thread for safe shared access.
 */
void platformLockAudio(void) {
    if (audioLockInitialized)
        EnterCriticalSection(&audioLock);
}

void platformUnlockAudio(void) {
    if (audioLockInitialized)
        LeaveCriticalSection(&audioLock);
}

int platformLoadWAVFromMemory(const uint8* data, uint32 dataSize,
                              PlatformAudioSpec* spec,
                              uint8** audio_buf, uint32* audio_len) {
    if (!data || dataSize < 44) {
        lastError = "Invalid WAV data (too small)";
        return -1;
    }

    uint32 wavDataSize = readLE32(data + 40);

    /* Clamp to actual buffer size (minus the 44-byte header) */
    if (wavDataSize > dataSize - 44)
        wavDataSize = dataSize - 44;

    *audio_len = wavDataSize;
    *audio_buf = (uint8*)malloc(wavDataSize);
    if (!*audio_buf) {
        lastError = "Failed to allocate WAV buffer";
        return -1;
    }

    memcpy(*audio_buf, data + 44, wavDataSize);

    spec->freq = (int)readLE32(data + 24);
    spec->channels = (uint8)readLE16(data + 22);
    spec->format = readLE16(data + 34);

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

#endif // PLATFORM_WINDOWS
