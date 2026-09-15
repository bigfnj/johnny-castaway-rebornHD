/* Actual events.c boundary behavior, with deterministic host and shutdown hooks. */
#undef NDEBUG
#include <assert.h>
#include <setjmp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "platform.h"

static jmp_buf stopped;
static int stopCode = -1, cleanupOrder, yields, polls;
static void testExit(int code);
#define exit testExit
#include "../src/engine/events.c"
#undef exit

static void testExit(int code) { stopCode = code; longjmp(stopped, 1); }
void soundEnd(void) { assert(cleanupOrder == 0); cleanupOrder = 1; }
void graphicsEnd(void) { assert(cleanupOrder == 1); cleanupOrder = 2; }
void grToggleFullScreen(void) { assert(!"unexpected fullscreen toggle"); }
void grRefreshDisplay(void) { assert(!"unexpected refresh"); }
uint32 platformGetTicks(void) { return 0; }
void platformDelay(uint32 ms) { (void)ms; assert(!"unexpected delay"); }
void platformFrameYield(void) { yields++; }
void platformShutdown(void) {}
int platformPollEvent(PlatformEvent *event) { (void)event; polls++; return 0; }

int main(int argc, char **argv)
{
    assert(argc == 2);
    printf("WITNESS events.c frame %s BEGIN\n", argv[1]); fflush(stdout);
    maxSpeed = 1;
    if (!strcmp(argv[1], "unlimited")) {
        evMaxFrames = 0;
        evFrameCount = UINT32_MAX;
        for (int i = 0; i < 3; i++) eventsWaitTick(0);
        assert(evFrameCount == UINT32_MAX && yields == 3 && polls == 3);
        assert(stopCode == -1 && cleanupOrder == 0);
    } else {
        volatile unsigned expectedCalls;
        if (!strcmp(argv[1], "ordinary")) {
            evMaxFrames = 3;
            evFrameCount = 0;
            expectedCalls = 3;
        } else if (!strcmp(argv[1], "maximum")) {
            evMaxFrames = UINT32_MAX;
            evFrameCount = UINT32_MAX - 1;
            expectedCalls = 1;
        } else { assert(!"unknown frame case"); return 2; }
        if (setjmp(stopped) == 0) {
            for (unsigned i = 0; i < expectedCalls; i++) eventsWaitTick(0);
            assert(evFrameCount == evMaxFrames && "last permitted frame returned");
            assert(cleanupOrder == 0 && stopCode == -1);
            eventsWaitTick(0);
            assert(!"frame limit did not stop on the next tick");
        }
        assert(stopCode == 0 && cleanupOrder == 2 && "clean bounded shutdown");
        assert(evFrameCount == evMaxFrames && "frame counter must not wrap");
        assert(yields == (int)expectedCalls && polls == (int)expectedCalls);
    }
    printf("WITNESS events.c frame %s PASS\n", argv[1]);
    return 0;
}
