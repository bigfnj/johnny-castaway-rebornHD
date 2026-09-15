/* Exercise the real backend worker with pthreads and deterministic ALSA faults. */
#include <assert.h>
#include <errno.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <alsa/asoundlib.h>

static int fail_create, fail_alloc, fail_params, fail_join, closes, drains, joins;
static atomic_int writes, callbacks, fail_write;
static int fake_open(snd_pcm_t **p, const char *n, snd_pcm_stream_t s, int m)
{ (void)n; (void)s; (void)m; *p = (snd_pcm_t *)(void *)&closes; return 0; }
static int fake_close(snd_pcm_t *p) { assert(p); closes++; return 0; }
static int fake_drain(snd_pcm_t *p) { assert(p); drains++; return 0; }
static int fake_any(snd_pcm_t *p, snd_pcm_hw_params_t *v)
{ (void)p; (void)v; return 0; }
static int fake_access(snd_pcm_t *p, snd_pcm_hw_params_t *v, snd_pcm_access_t a)
{ (void)p; (void)v; (void)a; return 0; }
static int fake_format(snd_pcm_t *p, snd_pcm_hw_params_t *v, snd_pcm_format_t f)
{ (void)p; (void)v; (void)f; return 0; }
static int fake_channels(snd_pcm_t *p, snd_pcm_hw_params_t *v, unsigned c)
{ (void)p; (void)v; assert(c == 1); return 0; }
static int fake_rate(snd_pcm_t *p, snd_pcm_hw_params_t *v, unsigned *r, int *d)
{ (void)p; (void)v; (void)d; assert(*r == 11025); return 0; }
static int fake_params(snd_pcm_t *p, snd_pcm_hw_params_t *v)
{ (void)p; (void)v; return fail_params ? -EINVAL : 0; }
static snd_pcm_sframes_t fake_write(snd_pcm_t *p, const void *b, snd_pcm_uframes_t n)
{ assert(p && b && n == 16); atomic_fetch_add(&writes, 1); usleep(1000); return atomic_load(&fail_write) ? -EIO : (snd_pcm_sframes_t)n; }
static int fake_recover(snd_pcm_t *p, int err, int silent)
{ assert(p && err == -EIO && silent); return -EIO; }
static int fake_create(pthread_t *t, const pthread_attr_t *a, void *(*f)(void *), void *p)
{ return fail_create ? EAGAIN : pthread_create(t, a, f, p); }
static int fake_join(pthread_t t, void **v)
{ joins++; return fail_join ? EDEADLK : pthread_join(t, v); }
static void *fake_malloc(size_t n) { return fail_alloc ? NULL : malloc(n); }

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
#define snd_pcm_recover fake_recover
#define pthread_create fake_create
#define pthread_join fake_join
#define malloc fake_malloc
#include "../platform/platform_linux.c"
#undef malloc

static void callback(void *p, uint8 *b, int n)
{
    assert(p == &callbacks && n == 16);
    platformLockAudio();
    memset(b, 128, (size_t)n);
    atomic_fetch_add(&callbacks, 1);
    platformUnlockAudio();
}
static void wait_for_write(void)
{
    for (int i = 0; i < 2000 && !atomic_load(&writes); i++) usleep(1000);
    assert(atomic_load(&writes));
}
static void closed_state(void)
{
    assert(!audioThreadCreated && !atomic_load(&audioThreadRunning));
    assert(!pcmHandle && !audioBuffer);
}
int main(int argc, char **argv)
{
    assert(argc == 2);
    printf("WITNESS platform_linux.c audio %s BEGIN\n", argv[1]); fflush(stdout);
    PlatformAudioSpec spec = {11025, 8, 1, 16, callback, &callbacks};
    if (!strcmp(argv[1], "worker-error")) {
        atomic_store(&fail_write, 1);
        assert(platformOpenAudio(&spec) == 0);
        wait_for_write();
        for (int i = 0; i < 2000 && atomic_load(&audioThreadRunning); i++) usleep(1000);
        assert(!atomic_load(&audioThreadRunning));
        assert(strstr(platformGetError(), "could not be recovered"));
        platformCloseAudio();
        assert(joins == 1 && closes == 1 && drains == 1);
        closed_state();
    } else if (!strcmp(argv[1], "normal-reopen")) {
        for (int i = 0; i < 2; i++) {
            atomic_store(&writes, 0);
            assert(platformOpenAudio(&spec) == 0);
            assert(platformOpenAudio(&spec) == -1);
            wait_for_write();
            platformCloseAudio();
            platformCloseAudio();
            closed_state();
        }
        assert(joins == 2 && closes == 2 && drains == 2);
    } else if (!strcmp(argv[1], "create-failure")) {
        fail_create = 1;
        assert(platformOpenAudio(&spec) == -1);
        platformCloseAudio();
        assert(joins == 0 && closes == 1 && drains == 0);
        closed_state();
    } else if (!strcmp(argv[1], "allocation-failure")) {
        fail_alloc = 1;
        assert(platformOpenAudio(&spec) == -1);
        platformCloseAudio();
        assert(joins == 0 && closes == 1 && drains == 0);
        closed_state();
    } else if (!strcmp(argv[1], "parameter-failure")) {
        fail_params = 1;
        assert(platformOpenAudio(&spec) == -1);
        platformCloseAudio();
        assert(joins == 0 && closes == 1 && drains == 0);
        closed_state();
    } else if (!strcmp(argv[1], "join-failure")) {
        assert(platformOpenAudio(&spec) == 0);
        wait_for_write();
        fail_join = 1;
        platformCloseAudio();
        assert(audioThreadCreated && pcmHandle && audioBuffer);
        assert(closes == 0 && drains == 0);
        fail_join = 0;
        platformCloseAudio();
        assert(joins == 2 && closes == 1 && drains == 1);
        closed_state();
    } else assert(!"unknown case");
    printf("WITNESS platform_linux.c audio %s PASS\n", argv[1]);
    return 0;
}
