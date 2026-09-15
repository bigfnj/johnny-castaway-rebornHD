#undef NDEBUG
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "../platform/platform_macos.m"

/* AppKit owns the queue; this delegate substitute makes dispatch deterministic
 * without creating a window or sending keystrokes to another application. */
@interface ProbeApplication : NSApplication
@end
@implementation ProbeApplication
- (void)sendEvent:(NSEvent *)event {
    if ([event type] == NSEventTypeApplicationDefined && [event subtype] == 1)
        quitRequested = 1;
}
@end

int main(int argc, char **argv) {
    assert(argc == 2);
    printf("WITNESS platform_macos.m events %s BEGIN\n", argv[1]); fflush(stdout);
    @autoreleasepool {
        [ProbeApplication sharedApplication];
        NSString *chars = !strcmp(argv[1], "unknown-key") ? @"" : @"m";
        NSEvent *key = [NSEvent keyEventWithType:NSEventTypeKeyDown location:NSZeroPoint
            modifierFlags:0 timestamp:0 windowNumber:0 context:nil characters:chars
            charactersIgnoringModifiers:chars isARepeat:NO keyCode:0];
        [NSApp postEvent:key atStart:NO];
        NSEvent *ignored = [NSEvent otherEventWithType:NSEventTypeApplicationDefined location:NSZeroPoint
            modifierFlags:0 timestamp:0 windowNumber:0 context:nil
            subtype:(!strcmp(argv[1], "delegate-quit") ? 1 : 0) data1:0 data2:0];
        [NSApp postEvent:ignored atStart:YES];
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
    }
    printf("WITNESS platform_macos.m events %s PASS\n", argv[1]);
    return 0;
}
