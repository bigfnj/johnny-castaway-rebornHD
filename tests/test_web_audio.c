#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "../platform/platform_web.c"
static int calls;
static void callback(void *userdata, uint8 *stream, int length) {
    assert(userdata == &calls && length == 4);
    const uint8 values[4] = {0, 64, 128, 255};
    memcpy(stream, values, 4);
    calls++;
}
int main(int argc, char **argv) {
    assert(argc == 2);
    printf("WITNESS platform_web.c audio %s BEGIN\n", argv[1]); fflush(stdout);
    EM_ASM({
        globalThis.window = {};
        window.audioContext = ({
            state: 'running', currentTime: 0,
            createBuffer: function(channels, frames, rate) {
                if (channels !== 1 || frames !== 4 || rate !== 11025) throw Error('channel/frame/rate contract');
                var values = new Float32Array(frames);
                return {getChannelData: function(channel) {
                    if (channel !== 0) throw Error('channel index');
                    window.observedSamples = values;
                    return values;
                }};
            },
            createBufferSource: function() { return {connect: function() {}, start: function(t) { window.lastStart = t; }}; },
            close: function() {}
        });
    });
    PlatformAudioSpec spec = {11025, 8, 1, 4, callback, &calls};
    assert(platformOpenAudio(&spec) == 0);
    uint8 *original = webAudioBuf;
    if (!strcmp(argv[1], "stereo")) {
        spec.channels = 2;
        assert(platformOpenAudio(&spec) == -1 && webAudioBuf == original);
    } else if (!strcmp(argv[1], "format")) {
        spec.format = 16;
        assert(platformOpenAudio(&spec) == -1 && webAudioBuf == original);
    } else assert(!strcmp(argv[1], "mono"));
    webAudioPump();
    assert(calls == 8); /* Existing bounded scheduling cadence. */
    assert(EM_ASM_INT({
        var a = window.observedSamples;
        return a[0] === -1 && a[1] === -0.5 && a[2] === 0 && a[3] === 127 / 128 &&
            Math.abs(window.jcAudioNext - 32 / 11025) < 1e-12;
    }));
    platformCloseAudio();
    assert(webAudioBuf == NULL && audioCallback == NULL);
    printf("WITNESS platform_web.c audio %s PASS\n", argv[1]);
    return 0;
}
