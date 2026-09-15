/* Real engine and Windows surface allocation, without creating a window.
 * Including ads.c exposes its private ownership state only to this test target.
 * The virtual clock affects benchmark timing only, not rendering or cleanup. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "platform.h"
#include "graphics.h"
#include "resource.h"
#include "events.h"
#include "sound.h"
#include "lifecycle_alloc.h"
static uint32 benchmarkTicks;
static uint32 lifecycleTicks(void) { benchmarkTicks += 1000; return benchmarkTicks; }
#define platformGetTicks lifecycleTicks
#include "../src/engine/ads.c"
#undef platformGetTicks

static const char *caseName;
static void require(int condition, const char *message)
{
    if (!condition) {
        fprintf(stderr, "CHECK %s: %s (live blocks=%zu bytes=%zu)\n",
                caseName, message, jcTestLiveBlocks(), jcTestLiveBytes());
        exit(1);
    }
}

static void fixture(void)
{
    require(platformInit() == 0, "platform clock initialized without a window");
    static uint8 pixels[8] = {0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88};
    static uint16 widths[] = {4}, heights[] = {4};
    static struct TBmpResource boat;
    static struct TScrResource ocean;
    static uint8 code[] = {0x04, 0x42, 0, 0, 0, 0, 2, 0, 2, 0, 0xf0, 0x0f};
    static struct TTtmResource script;
    boat.resName = "BOAT.BMP";
    boat.numImages = 1;
    boat.widths = widths;
    boat.heights = heights;
    boat.uncompressedData = pixels;
    boat.uncompressedSize = sizeof(pixels);
    bmpResources[0] = &boat;
    numBmpResources = 1;
    ocean.resName = "OCEAN00.SCR";
    ocean.width = ocean.height = 4;
    ocean.uncompressedData = pixels;
    ocean.uncompressedSize = sizeof(pixels);
    scrResources[0] = &ocean;
    numScrResources = 1;
    script.resName = "SAVE.TTM";
    script.uncompressedData = code;
    script.uncompressedSize = sizeof(code);
    ttmResources[0] = &script;
    numTtmResources = 1;
    grScale = 1;
    grRenderWidth = grRenderHeight = 64;
    grHdEnabled = 0;
    soundDisabled = 1;
    evStartAtMaxSpeed = 1;
    eventsInit();
}

static void sceneRelease(void)
{
    adsInit();
    ttmThreads[0].ttmLayer = grNewLayer();
    ttmThreads[0].isRunning = TTM_FREE;
    ttmThreads[1].ttmLayer = grNewLayer();
    ttmThreads[1].isRunning = TTM_RUNNING;
    numThreads = 1;
    require(jcTestLiveBlocks() == 4, "two real owned surfaces were allocated");
    adsStopScene(0);
    require(numThreads == 1 && !ttmThreads[0].ttmLayer && jcTestLiveBlocks() == 2,
            "inactive owner released without decrementing active count");
    adsStopScene(0);
    adsStopScene(1);
    adsStopScene(1);
    require(numThreads == 0 && !ttmThreads[1].ttmLayer && jcTestLiveBlocks() == 0,
            "active release is idempotent and decrements once");
}

static void benchmarkRelease(void)
{
    adsPlayBench();
    require(benchmarkTicks >= 12000, "all real benchmark phases executed");
    for (int i = 0; i < MAX_TTM_THREADS; i++)
        require(!ttmThreads[i].ttmLayer, "benchmark released every allocated layer");
    require(jcTestLiveBlocks() == 2, "only the graphics-owned background remains");
    graphicsEnd();
    require(jcTestLiveBlocks() == 0, "benchmark and graphics allocations released");
}

static void standaloneRelease(void)
{
    adsPlaySingleTtm("SAVE.TTM");
    require(jcTestTotalAllocations() >= 5, "script actually allocated a saved layer and scene/tag state");
    require(jcTestLiveBlocks() == 0, "standalone TTM releases its saved-zone layer");
}

static void reinitialize(void)
{
    adsInit();
    grInitEmptyBackground();
    PlatformSurface *background = grBackgroundSfc;
    const void *pixels = platformGetSurfacePixels(background);
    size_t baseline = jcTestLiveBlocks();
    require(baseline == 2, "background fixture allocated pixels and borrowed surface wrapper");
    ttmBackgroundThread.ttmLayer = background;
    ttmBackgroundThread.isRunning = TTM_STATIC_LAYER;
    ttmCloudsThread.ttmLayer = grNewLayer();
    ttmCloudsThread.isRunning = TTM_FREE;
    ttmHolidayThread.ttmLayer = grNewLayer();
    ttmHolidayThread.isRunning = TTM_FREE;
    ttmThreads[0].ttmLayer = grNewLayer();
    ttmThreads[0].isRunning = TTM_RUNNING;
    numThreads = 1;
    grLoadBmp(&ttmSlots[0], 0, "BOAT.BMP");
    grLoadBmp(&ttmBackgroundSlot, 0, "BOAT.BMP");
    grLoadBmp(&ttmCloudsSlot, 0, "BOAT.BMP");
    ttmSlots[0].tags = safe_malloc(sizeof(struct TTtmTag));
    ttmSlots[0].numTags = 1;
    ttmSlots[0].bmpNames[1] = safe_malloc(5);  /* cached name with zero sprites */
    adsTags = safe_malloc(sizeof(struct TTtmTag));
    adsNumTags = 1;
    grCopyZoneToBg(ttmThreads[0].ttmLayer, 0, 0, 2, 2);
    require(jcTestLiveBlocks() > baseline + 12, "reinitialization fixture owns all resource categories");
    adsInit();
    require(jcTestLiveBlocks() == baseline, "reinitialization releases owned layers, slots, ADS tags and saved zones");
    require(jcTestIsLive(background) && jcTestIsLive(pixels) && grBackgroundSfc == background,
            "background alias was cleared without freeing the graphics owner");
    require(!ttmBackgroundThread.ttmLayer && !ttmCloudsThread.ttmLayer && !ttmHolidayThread.ttmLayer,
            "island aliases and owner pointers cleared");
    require(!ttmSlots[0].tags && !ttmSlots[0].bmpNames[0] && !ttmSlots[0].bmpNames[1], "slot reset clears pointer state");
    adsInit();
    adsReleaseIsland();
    require(jcTestLiveBlocks() == baseline, "repeated release and initialization are idempotent");
    graphicsEnd();
    require(jcTestLiveBlocks() == 0, "graphics releases its remaining background owner");
}

static void graphicsRelease(void)
{
    grInitEmptyBackground();
    PlatformSurface *layer = grNewLayer();
    grCopyZoneToBg(layer, 0, 0, 2, 2);
    grFreeLayer(layer);
    require(jcTestLiveBlocks() == 4, "graphics fixture owns a background and saved layer");
    graphicsEnd();
    require(!grBackgroundSfc && jcTestLiveBlocks() == 0, "graphics teardown releases both owners");
    graphicsEnd();
    require(jcTestLiveBlocks() == 0, "repeated graphics teardown is idempotent");
}

int main(int argc, char **argv)
{
    if (argc != 2) return 2;
    caseName = argv[1];
    printf("WITNESS production lifecycle executed: %s\n", caseName);
    fflush(stdout);
    fixture();
    if (!strcmp(caseName, "scene-release")) sceneRelease();
    else if (!strcmp(caseName, "benchmark-release")) benchmarkRelease();
    else if (!strcmp(caseName, "standalone-saved-zone")) standaloneRelease();
    else if (!strcmp(caseName, "reinitialize")) reinitialize();
    else if (!strcmp(caseName, "graphics-release")) graphicsRelease();
    else return 2;
    require(jcTestLiveBlocks() == 0 && jcTestLiveBytes() == 0, "test ends with no owned allocations");
    printf("RESULT %s allocations=%zu live=%zu bytes=%zu\n", caseName,
           jcTestTotalAllocations(), jcTestLiveBlocks(), jcTestLiveBytes());
    return 0;
}
