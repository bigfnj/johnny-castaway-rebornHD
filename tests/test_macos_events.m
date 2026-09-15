#undef NDEBUG
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "../platform/platform_macos.m"

/* Real NSEvent objects in a controlled queue exercise the production poll loop.
 * AppKit may discard synthetic keys for windowNumber=0 before an application
 * launches, so this probe does not claim to test OS key delivery. */
static NSEvent *queuedEvents[2];
static unsigned queuedCount, nextQueued, dispatched;
@interface ProbeApplication : NSApplication
@end
@implementation ProbeApplication
- (NSEvent *)nextEventMatchingMask:(NSEventMask)mask
                       untilDate:(NSDate *)expiration
                          inMode:(NSRunLoopMode)mode
                         dequeue:(BOOL)dequeue {
    (void)expiration;
    assert(mask == NSEventMaskAny && [mode isEqualToString:NSDefaultRunLoopMode]);
    assert(dequeue);
    return nextQueued < queuedCount ? queuedEvents[nextQueued++] : nil;
}
- (void)sendEvent:(NSEvent *)event {
    dispatched++;
    if ([event type] == NSEventTypeApplicationDefined && [event subtype] == 1)
        quitRequested = 1;
}
@end

int main(int argc, char **argv) {
    assert(argc == 2);
    printf("WITNESS platform_macos.m events %s BEGIN\n", argv[1]); fflush(stdout);
    @autoreleasepool {
        [ProbeApplication sharedApplication];
        assert([NSApp isKindOfClass:[ProbeApplication class]]);
        NSString *chars = !strcmp(argv[1], "unknown-key") ? @"" : @"m";
        NSEvent *key = [NSEvent keyEventWithType:NSEventTypeKeyDown location:NSZeroPoint
            modifierFlags:0 timestamp:0 windowNumber:0 context:nil characters:chars
            charactersIgnoringModifiers:chars isARepeat:NO keyCode:0];
        NSEvent *ignored = [NSEvent otherEventWithType:NSEventTypeApplicationDefined location:NSZeroPoint
            modifierFlags:0 timestamp:0 windowNumber:0 context:nil
            subtype:(!strcmp(argv[1], "delegate-quit") ? 1 : 0) data1:0 data2:0];
        assert(key && ignored);
        queuedEvents[0] = ignored;
        queuedEvents[1] = key;
        queuedCount = 2;
        PlatformEvent event = {0};
        event.data.key.keycode = KEY_M;
        assert(platformPollEvent(&event));
        if (!strcmp(argv[1], "delegate-quit")) {
            assert(event.type == EVENT_QUIT && !quitRequested);
            assert(platformPollEvent(&event) && event.type == EVENT_KEY_DOWN);
        } else {
            assert(event.type == EVENT_KEY_DOWN);
            assert(event.data.key.keycode == (!strcmp(argv[1], "unknown-key") ? KEY_UNKNOWN : KEY_M));
        }
        assert(!platformPollEvent(&event));
        assert(nextQueued == queuedCount && dispatched == 2);
    }
    printf("WITNESS platform_macos.m events %s PASS\n", argv[1]);
    return 0;
}
