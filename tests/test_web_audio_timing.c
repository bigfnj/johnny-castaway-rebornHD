/* Real Web scheduling and engine waits; only the host clock/sleep are controlled. */
#undef NDEBUG
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <emscripten.h>
#include <emscripten/html5.h>

static double testNow(void);
static void testSleep(unsigned int ms);
#define emscripten_get_now testNow
#define emscripten_sleep testSleep
#include "../platform/platform_web.c"
#undef emscripten_get_now
#undef emscripten_sleep
#include "../src/engine/events.c"

void soundEnd(void) { assert(!"unexpected sound shutdown"); }
void graphicsEnd(void) { assert(!"unexpected graphics shutdown"); }
void grToggleFullScreen(void) { assert(!"unexpected fullscreen request"); }
void grRefreshDisplay(void) { assert(!"unexpected display refresh"); }

static unsigned sampleIndex, callbacks, zeroSleeps, timedSleeps;
static double testNow(void) { return EM_ASM_DOUBLE({ return window.jcTestNow; }); }
static void testSleep(unsigned int ms) {
    if (ms) timedSleeps++; else zeroSleeps++;
    EM_ASM({
        window.jcTestNow += $0;
        var ctx = window.audioContext;
        if (ctx && ctx.state === 'running') {
            ctx.currentTime += $0 / 1000;
            if (window.jcCheckCoverage && ctx.currentTime > window.jcLastEnd + 1e-9)
                throw Error('platform_web.c: timed wait audio continuity');
        }
    }, ms);
}
static void callback(void *userdata, uint8 *stream, int length) {
    assert(userdata == &callbacks && length == 1024);
    for (int i = 0; i < length; i++, sampleIndex++)
        stream[i] = (uint8)(sampleIndex * 17 + sampleIndex / 251);
    callbacks++;
}
static void setup(void) {
    EM_ASM({
        globalThis.window = {};
        window.jcTestNow = 1000;
        window.jcLastEnd = 1;
        window.jcScheduled = 0;
        window.jcSampleIndex = 0;
        window.jcCheckCoverage = false;
        window.audioContext = ({
            state: 'running', currentTime: 1,
            createBuffer: function(channels, frames, rate) {
                if (channels !== 1 || frames !== 1024 || rate !== 11025)
                    throw Error('platform_web.c: timing PCM format');
                var values = new Float32Array(frames);
                return {duration: frames / rate, values: values, getChannelData: function(channel) {
                    if (channel !== 0) throw Error('platform_web.c: timing PCM channel');
                    return values;
                }};
            },
            createBufferSource: function() { return {
                connect: function() {},
                start: function(t) {
                    var ctx = window.audioContext;
                    if (ctx.state !== 'running') throw Error('platform_web.c: suspended callback consumption');
                    if (Math.abs(t - window.jcLastEnd) > 1e-9)
                        throw Error('platform_web.c: scheduled buffers are not contiguous');
                    if (t < ctx.currentTime - 1e-9)
                        throw Error('platform_web.c: scheduled buffer starts in the past');
                    var values = this.buffer.values;
                    for (var i = 0; i < values.length; i++) {
                        var n = window.jcSampleIndex++;
                        var expected = (((n * 17 + Math.floor(n / 251)) & 255) - 128) / 128;
                        if (values[i] !== expected) throw Error('platform_web.c: timing PCM sample order');
                    }
                    window.jcLastEnd = t + this.buffer.duration;
                    window.jcScheduled++;
                    if (window.jcLastEnd - ctx.currentTime > 0.25 + 1024 / 11025 + 1e-9)
                        throw Error('platform_web.c: audio lookahead bound');
                }
            }; },
            suspend: function() { this.state = 'suspended'; },
            resume: function() { this.state = 'running'; },
            close: function() { this.state = 'closed'; }
        });
    });
    PlatformAudioSpec spec = {11025, 8, 1, 1024, callback, &callbacks};
    assert(platformOpenAudio(&spec) == 0);
    eventsInit();
}
int main(int argc, char **argv) {
    assert(argc == 2);
    printf("WITNESS platform_web.c timing %s BEGIN\n", argv[1]); fflush(stdout);
    if (!strcmp(argv[1], "maxspeed")) evStartAtMaxSpeed = 1;
    setup();
    if (!strcmp(argv[1], "timed-wait")) {
        EM_ASM({ window.jcCheckCoverage = true; });
        eventsWaitTick(50);
        assert(testNow() == 2000 && timedSleeps == 200 && zeroSleeps == 1);
        assert(callbacks > 10 && "platform_web.c: callbacks continue during long wait");
    } else if (!strcmp(argv[1], "suspended")) {
        platformPauseAudio(1);
        eventsWaitTick(50);
        assert(callbacks == 0 && "platform_web.c: suspended callback consumption");
        platformPauseAudio(0);
        EM_ASM({ window.jcCheckCoverage = true; });
        eventsWaitTick(50);
        assert(callbacks > 10 && "platform_web.c: resumed wait did not refill");
    } else if (!strcmp(argv[1], "closed")) {
        platformCloseAudio();
        eventsWaitTick(50);
        assert(callbacks == 0 && "platform_web.c: closed callback consumption");
    } else if (!strcmp(argv[1], "maxspeed")) {
        eventsWaitTick(50);
        assert(callbacks > 0 && "platform_web.c: maxspeed frame does not schedule audio");
        assert(timedSleeps == 0 && zeroSleeps == 1 && testNow() == 1000);
    } else assert(!"unknown timing case");
    platformCloseAudio();
    assert(!webAudioBuf && !audioCallback);
    printf("WITNESS platform_web.c timing %s PASS callbacks=%u timed-sleeps=%u\n",
           argv[1], callbacks, timedSleeps);
    return 0;
}
