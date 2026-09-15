/* Real pthread worker and setup code with controlled ALSA device responses. */
#undef NDEBUG
#include <assert.h>
#include <errno.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <alsa/asoundlib.h>

static const char *scenario;
static int failStage, stage, channels = 1, opens, closes, drains, creates, joins;
static int writeCalls, waitCalls, recoverCalls, delivered;
static unsigned char deliveredBytes[32];
static atomic_int callbacks, waiting;
static int fake_open(snd_pcm_t **p, const char *n, snd_pcm_stream_t s, int mode)
{ (void)n; (void)s; (void)mode; opens++; *p = (snd_pcm_t *)(void *)&opens; return 0; }
static int fake_close(snd_pcm_t *p) { assert(p); closes++; return 0; }
static int fake_drain(snd_pcm_t *p) { assert(p); drains++; return 0; }
static int next_stage(void) { stage++; return stage == failStage ? -EINVAL : 0; }
static int fake_any(snd_pcm_t *p, snd_pcm_hw_params_t *v)
{ assert(p && v); return next_stage(); }
static int fake_access(snd_pcm_t *p, snd_pcm_hw_params_t *v, snd_pcm_access_t a)
{ assert(p && v && a == SND_PCM_ACCESS_RW_INTERLEAVED); return next_stage(); }
static int fake_format(snd_pcm_t *p, snd_pcm_hw_params_t *v, snd_pcm_format_t f)
{ assert(p && v && f == SND_PCM_FORMAT_U8); return next_stage(); }
static int fake_channels(snd_pcm_t *p, snd_pcm_hw_params_t *v, unsigned c)
{ assert(p && v && c == (unsigned)channels); return next_stage(); }
static int fake_rate(snd_pcm_t *p, snd_pcm_hw_params_t *v, unsigned *r, int *dir)
{
    (void)dir;
    assert(p && v && *r == 11025);
    if (!strcmp(scenario, "rate-near")) *r = 22050;
    return next_stage();
}
static int fake_params(snd_pcm_t *p, snd_pcm_hw_params_t *v)
{ assert(p && v); return next_stage(); }
static int fake_create(pthread_t *t, const pthread_attr_t *a, void *(*f)(void *), void *p)
{ creates++; return pthread_create(t, a, f, p); }
static int fake_join(pthread_t t, void **v) { joins++; return pthread_join(t, v); }
static snd_pcm_sframes_t fake_write(snd_pcm_t *, const void *, snd_pcm_uframes_t);
static int fake_wait(snd_pcm_t *, int);
static int fake_recover(snd_pcm_t *, int, int);

#define snd_pcm_open fake_open
#define snd_pcm_close fake_close
#define snd_pcm_drain fake_drain
#define snd_pcm_hw_params_any fake_any
#define snd_pcm_hw_params_set_access fake_access
#define snd_pcm_hw_params_set_format fake_format
#define snd_pcm_hw_params_set_channels fake_channels
#define snd_pcm_hw_params_set_rate_near fake_rate
#define snd_pcm_hw_params fake_params
#define snd_pcm_writei fake_write
#define snd_pcm_wait fake_wait
#define snd_pcm_recover fake_recover
#define pthread_create fake_create
#define pthread_join fake_join
#include "../platform/platform_linux.c"

static void callback(void *p, uint8 *buffer, int size)
{
    assert(p == &callbacks && size == 16 * channels);
    assert(atomic_fetch_add(&callbacks, 1) == 0 && "callback must not replace an unwritten tail");
    platformLockAudio();
    for (int i = 0; i < size; i++) buffer[i] = (uint8)(i + 17);
    platformUnlockAudio();
}

static snd_pcm_sframes_t fake_write(snd_pcm_t *p, const void *buffer, snd_pcm_uframes_t frames)
{
    const uint8 *bytes = buffer;
    assert(p && frames == (snd_pcm_uframes_t)(16 - delivered));
    for (unsigned i = 0; i < frames * (unsigned)channels; i++)
        assert(bytes[i] == (uint8)(17 + delivered * channels + (int)i)
               && "write tail has the wrong byte offset");
    writeCalls++;
    assert(writeCalls <= 6 && "worker retried after stop or discarded recovery state");
    if (!strcmp(scenario, "blocked-stop")) return 0;
    if (writeCalls == 2) {
        if (!strcmp(scenario, "recover") || !strcmp(scenario, "recover-failure")) return -EPIPE;
        if (!strcmp(scenario, "interrupted")) return -EINTR;
        if (!strcmp(scenario, "would-block") || !strcmp(scenario, "wait-failure")) return -EAGAIN;
        if (!strcmp(scenario, "zero-progress") || !strcmp(scenario, "close-pending")) return 0;
    }
    int take = (int)frames;
    if (strcmp(scenario, "full") && strcmp(scenario, "rate-near")) {
        if (writeCalls == 1) take = 5;
        else if ((!strcmp(scenario, "partial-mono") || !strcmp(scenario, "partial-stereo")) && writeCalls == 2) take = 3;
    }
    memcpy(deliveredBytes + delivered * channels, bytes, (size_t)take * channels);
    delivered += take;
    /* The fixture device ends after one complete callback block. Ordinary
     * continuous playback and close/reopen are covered by test_linux_audio.c. */
    if (delivered == 16) atomic_store(&audioThreadRunning, 0);
    return take;
}

static int fake_wait(snd_pcm_t *p, int timeout)
{
    assert(p && timeout == 20);
    waitCalls++;
    if (!strcmp(scenario, "close-pending")) {
        atomic_store(&waiting, 1);
        for (int i = 0; i < 2000 && atomic_load(&audioThreadRunning); i++) usleep(1000);
        assert(!atomic_load(&audioThreadRunning) && "concurrent close did not stop the pending write");
        return 0;
    }
    if (!strcmp(scenario, "blocked-stop")) {
        assert(waitCalls <= 3 && "pending write ignored shutdown");
        if (waitCalls == 3) atomic_store(&audioThreadRunning, 0);
        return 0;
    }
    if (!strcmp(scenario, "wait-failure")) return -EIO;
    return !strcmp(scenario, "zero-progress") ? 0 : 1;
}

static int fake_recover(snd_pcm_t *p, int error, int silent)
{
    assert(p && silent == 1);
    recoverCalls++;
    if (!strcmp(scenario, "wait-failure")) { assert(error == -EIO); return -EIO; }
    if (!strcmp(scenario, "interrupted")) { assert(error == -EINTR); return 0; }
    assert(error == -EPIPE);
    return !strcmp(scenario, "recover-failure") ? -EIO : 0;
}

static void closed_state(void)
{
    assert(!audioThreadCreated && !atomic_load(&audioThreadRunning));
    assert(!pcmHandle && !audioBuffer && !audioBufferSize && !audioFrames && !audioFrameBytes);
    assert(!audioCallback && !audioUserData);
}

int main(int argc, char **argv)
{
    assert(argc == 2);
    scenario = argv[1];
    printf("WITNESS platform_linux.c delivery %s BEGIN\n", scenario); fflush(stdout);
    const char *names[] = {"any-failure", "access-failure", "format-failure", "channels-failure", "rate-failure", "commit-failure"};
    const char *errors[] = {"initialize ALSA parameters", "ALSA access mode", "ALSA sample format", "ALSA channels", "ALSA sample rate", "set ALSA parameters"};
    for (int i = 0; i < 6; i++) if (!strcmp(scenario, names[i])) failStage = i + 1;
    if (!strcmp(scenario, "partial-stereo") || !strcmp(scenario, "recover") ||
        !strcmp(scenario, "would-block") || !strcmp(scenario, "interrupted")) channels = 2;
    PlatformAudioSpec spec = {11025, 8, (uint8)channels, 16, callback, &callbacks};
    if (failStage) {
        assert(platformOpenAudio(&spec) == -1 && "failed setup must refuse audio open");
        assert(stage == failStage && "setup must stop at the failed setter");
        assert(strstr(platformGetError(), errors[failStage - 1]));
        platformCloseAudio();
        closed_state();
        assert(opens == 1 && closes == 1 && !drains && !creates && !joins && !atomic_load(&callbacks));
        /* A failed setup must not poison a later open. */
        failStage = stage = 0;
        scenario = "full";
        assert(platformOpenAudio(&spec) == 0);
    } else {
        assert(platformOpenAudio(&spec) == 0);
    }
    if (!strcmp(scenario, "close-pending")) {
        for (int i = 0; i < 2000 && !atomic_load(&waiting); i++) usleep(1000);
        assert(atomic_load(&waiting) && "worker did not reach a pending tail");
    } else {
        for (int i = 0; i < 2000 && atomic_load(&audioThreadRunning); i++) usleep(1000);
        assert(!atomic_load(&audioThreadRunning) && "device scenario did not finish");
    }
    platformCloseAudio();
    platformCloseAudio();
    closed_state();
    assert(creates == 1 && joins == 1 && drains == 1 && closes == opens && atomic_load(&callbacks) == 1);
    if (!strcmp(scenario, "recover-failure") || !strcmp(scenario, "wait-failure")) {
        assert(delivered == 5 && recoverCalls == 1);
        assert(strstr(platformGetError(), "could not be recovered"));
    } else if (!strcmp(scenario, "blocked-stop")) {
        assert(delivered == 0 && waitCalls == 3 && writeCalls == 3 && !recoverCalls);
    } else if (!strcmp(scenario, "close-pending")) {
        assert(delivered == 5 && waitCalls == 1 && writeCalls == 2 && !recoverCalls
               && "no pending-tail write after concurrent close");
    } else {
        assert(delivered == 16 && "complete callback buffer must be delivered");
        for (int i = 0; i < 16 * channels; i++) assert(deliveredBytes[i] == (uint8)(17 + i));
        if (!strcmp(scenario, "partial-mono") || !strcmp(scenario, "partial-stereo")) assert(writeCalls == 3);
        if (!strcmp(scenario, "recover") || !strcmp(scenario, "interrupted")) assert(recoverCalls == 1 && writeCalls == 3);
        if (!strcmp(scenario, "would-block") || !strcmp(scenario, "zero-progress")) assert(waitCalls == 1 && writeCalls == 3);
        assert(spec.freq == (!strcmp(scenario, "rate-near") ? 22050 : 11025));
    }
    printf("WITNESS platform_linux.c delivery %s PASS\n", argv[1]);
    return 0;
}
