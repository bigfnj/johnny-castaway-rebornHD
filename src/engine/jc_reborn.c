/*
 *  This file is part of 'Johnny Reborn'
 *
 *  An open-source engine for the classic
 *  'Johnny Castaway' screensaver by Sierra.
 *
 *  Copyright (C) 2019 Jeremie GUILLAUME
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program.  If not, see <https://www.gnu.org/licenses/>.
 *
 */

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <time.h>

#if defined(_WIN32)
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <windows.h>
#endif

#include "mytypes.h"
#include "utils.h"
#include "resource.h"
#include "dump.h"
#include "graphics.h"
#include "events.h"
#include "sound.h"
#include "ttm.h"
#include "ads.h"
#include "story.h"
#include "zipvfs.h"

#define MAX_ARGS 3

static int  argDump     = 0;
static int  argBench    = 0;
static int  argTtm      = 0;
static int  argAds      = 0;
static int  argPlayAll  = 0;
static int  argIsland   = 0;
static int  argMinimize = 0;

static char *args[MAX_ARGS];
static int  numArgs  = 0;


static int isMinimizeArg(const char *arg)
{
    if (!arg) return 0;
    return (!strcmp(arg, "minimize") ||
            !strcmp(arg, "-minimize") ||
            !strcmp(arg, "--minimize") ||
            !strcmp(arg, "/minimize"));
}

static void normalizeToken(const char *in, char *out, size_t outSize)
{
    size_t j = 0;
    if (!out || outSize == 0)
        return;

    if (!in) {
        out[0] = '\0';
        return;
    }

    for (size_t i = 0; in[i] && (j + 1) < outSize; i++) {
        unsigned char c = (unsigned char)in[i];
        if (isalnum(c)) {
            out[j++] = (char)tolower(c);
        }
    }

    out[j] = '\0';
}

static int pickRandomHoliday(void)
{
    // We pick a single random holiday at startup.
    // Keep it independent from the main rand() stream, which is seeded later
    // (graphicsInit()), so this doesn't perturb story/scene randomness.
    unsigned long long t = (unsigned long long)time(NULL);
    unsigned long long c = (unsigned long long)clock();
    unsigned long long mix = t ^ (t >> 32) ^ c ^ (c << 16);
    unsigned int x = (unsigned int)(mix ^ (mix >> 32));

    // 1..4 map to: Halloween, St Patrick, Christmas, New Year
    return 1 + (int)(x % 4);
}

static int parseHolidayToken(const char *arg, int *outHoliday)
{
    if (!arg || !outHoliday)
        return 0;

    char tok[64];
    normalizeToken(arg, tok, sizeof(tok));
    if (!tok[0])
        return 0;

    // Accept numeric 0..4
    if (tok[0] >= '0' && tok[0] <= '4' && tok[1] == '\0') {
        *outHoliday = tok[0] - '0';
        return 1;
    }

    // Automatic (calendar-based)
    if (!strcmp(tok, "auto") || !strcmp(tok, "calendar") ||
        !strcmp(tok, "date") || !strcmp(tok, "system")) {
        *outHoliday = -1;
        return 1;
    }

    // Choose a random holiday at startup
    if (!strcmp(tok, "random") || !strcmp(tok, "rand") || !strcmp(tok, "any")) {
        *outHoliday = -2;
        return 1;
    }

    // Explicitly disable
    if (!strcmp(tok, "none") || !strcmp(tok, "no") ||
        !strcmp(tok, "off") || !strcmp(tok, "noholiday")) {
        *outHoliday = 0;
        return 1;
    }

    // Supported holidays (see story.c / island.c)
    if (!strcmp(tok, "halloween")) {
        *outHoliday = 1;
        return 1;
    }

    if (!strcmp(tok, "stpatricks") || !strcmp(tok, "stpatrick") ||
        !strcmp(tok, "stpatricksday") || !strcmp(tok, "stpatrickday")) {
        *outHoliday = 2;
        return 1;
    }

    if (!strcmp(tok, "christmas") || !strcmp(tok, "xmas")) {
        *outHoliday = 3;
        return 1;
    }

    if (!strcmp(tok, "newyear") || !strcmp(tok, "newyears") ||
        !strcmp(tok, "newyearseve")) {
        *outHoliday = 4;
        return 1;
    }

    return 0;
}

static int isHolidayArg(const char *arg)
{
    if (!arg)
        return 0;

    return (!strcmp(arg, "holiday") ||
            !strcmp(arg, "-holiday") ||
            !strcmp(arg, "--holiday") ||
            !strcmp(arg, "/holiday"));
}


static void minimizeConsoleWindow(void)
{
#if defined(_WIN32)
    HWND console = GetConsoleWindow();
    if (!console) {
        return;
    }

    /*
     * If the user explicitly asks for "minimize", do it unconditionally.
     * (Heuristics based on console ownership are surprising for explicit
     * opt-in use cases like shortcuts, startup scripts, etc.)
     */
    ShowWindow(console, SW_MINIMIZE);
#endif
}


static void usage(void)
{
    printf("\n");
    printf(" Usage :\n");
    printf("         jc_reborn\n");
    printf("         jc_reborn help\n");
    printf("         jc_reborn version\n");
    printf("         jc_reborn dump\n");
    printf("         jc_reborn [<options>] bench\n");
    printf("         jc_reborn [<options>] ttm <TTM name>\n");
    printf("         jc_reborn [<options>] ads <ADS name> <ADS tag no>\n");
    printf("\n");
    printf(" Available options are:\n");
    printf("         window     - play in windowed mode\n");
    printf("         minimize   - start with the console window minimized (Windows)\n");
    printf("         nosound    - quiet mode\n");
    printf("         island     - display the island as background for ADS play\n");
    printf("         debug      - print some debug info on stdout\n");
    printf("         hotkeys    - enable hot keys\n");
    printf("         holiday <name> - force holiday decorations (halloween|stpatricks|christmas|newyear|random|none|auto)\n");
    printf("         (shorthand) halloween|stpatricks|christmas|newyear|random\n");
    printf("\n");
    printf(" While-playing hot-keys (if enabled):\n");
    printf("         Esc        - Terminate immediately\n");
    printf("         Alt+Return - Toggle full screen / windowed mode\n");
    printf("         Space      - Toggle pause / unpause\n");
    printf("         Return     - When paused, advance one frame\n");
    printf("         <M>        - toggle max / normal speed\n");
    printf("\n");
    exit(1);
}


static void version(void)
{
    printf("\n");
    printf("    Johnny Reborn, an open-source engine for\n");
    printf("    the classic Johnny Castaway screensaver by Sierra.\n");
    printf("    Development version Copyright (C) 2019 Jeremie GUILLAUME\n");
    printf("\n");
    exit(0);
}


static void parseArgs(int argc, char **argv)
{
    typedef enum {
        EXPECT_NONE = 0,
        EXPECT_TTM_NAME,
        EXPECT_ADS_NAME,
        EXPECT_ADS_TAG,
        EXPECT_HOLIDAY
    } TExpectedArg;

    TExpectedArg expect = EXPECT_NONE;

    for (int i=1; i < argc; i++) {

        if (expect != EXPECT_NONE) {
            switch (expect) {

                case EXPECT_TTM_NAME:
                    if (numArgs < MAX_ARGS)
                        args[numArgs++] = argv[i];
                    expect = EXPECT_NONE;
                    break;

                case EXPECT_ADS_NAME:
                    if (numArgs < MAX_ARGS)
                        args[numArgs++] = argv[i];
                    expect = EXPECT_ADS_TAG;
                    break;

                case EXPECT_ADS_TAG:
                    if (numArgs < MAX_ARGS)
                        args[numArgs++] = argv[i];
                    expect = EXPECT_NONE;
                    break;

                case EXPECT_HOLIDAY: {
                    int holiday = -1;
                    if (!parseHolidayToken(argv[i], &holiday))
                        fatalError("Unknown holiday '%s' (try: halloween, stpatricks, christmas, newyear, random, none, auto)", argv[i]);
                    if (holiday == -2)
                        holiday = pickRandomHoliday();
                    storySetForcedHoliday(holiday);
                    expect = EXPECT_NONE;
                    break;
                }

                default:
                    expect = EXPECT_NONE;
                    break;
            }
            continue;
        }

        if (!strcmp(argv[i], "help")) {
            usage();
        }
        else if (!strcmp(argv[i], "version")) {
            version();
        }
        else if (!strcmp(argv[i], "dump")) {
            argDump = 1;
        }
        else if (!strcmp(argv[i], "bench")) {
            argBench = 1;
        }
        else if (!strcmp(argv[i], "ttm")) {
            argTtm = 1;
            expect = EXPECT_TTM_NAME;
        }
        else if (!strcmp(argv[i], "ads")) {
            argAds = 1;
            expect = EXPECT_ADS_NAME;
        }
        else if (!strcmp(argv[i], "window")) {
            grWindowed = 1;
        }
        else if (isMinimizeArg(argv[i])) {
            argMinimize = 1;
        }
        else if (!strcmp(argv[i], "nosound")) {
            soundDisabled = 1;
        }
        else if (!strcmp(argv[i], "island")) {
            argIsland = 1;
        }
        else if (!strcmp(argv[i], "debug")) {
            debugMode = 1;
        }
        else if (!strcmp(argv[i], "hotkeys")) {
            evHotKeysEnabled = 1;
        }
        else if (isHolidayArg(argv[i])) {
            expect = EXPECT_HOLIDAY;
        }
        else {
            // Shorthand: allow passing the holiday name directly
            // (e.g. `jc_reborn christmas`)
            int holiday = -1;
            if (parseHolidayToken(argv[i], &holiday)) {
                if (holiday == -2)
                    storySetForcedHoliday(pickRandomHoliday());
                else if (holiday >= 0)
                    storySetForcedHoliday(holiday);
            }
        }
    }

    if (expect != EXPECT_NONE)
        usage();

    if (argDump + argBench + argTtm + argAds > 1)
        usage();

    if (argDump + argBench + argTtm + argAds == 0)
        argPlayAll = 1;
}


int main(int argc, char **argv)
{
    parseArgs(argc, argv);

    if (argDump)
        debugMode = 1;

    zipvfs_init("scrantic_data.zip");
    parseResourceFiles("data/RESOURCE.MAP");

    if (argPlayAll) {
        graphicsInit();

        if (argMinimize)
            minimizeConsoleWindow();

        soundInit();

        storyPlay();
        // NOTE: storyPlay() never returns (it loops forever and terminates
        // via exit() when input/quit events are received). Cleanup is handled
        // on the exit paths.
    }

    else if (argDump) {
        dumpAllResources();
    }

    else if (argBench) {
        graphicsInit();

        if (argMinimize)
            minimizeConsoleWindow();

        adsPlayBench();
        graphicsEnd();
    }

    else if (argTtm) {
        graphicsInit();

        if (argMinimize)
            minimizeConsoleWindow();

        soundInit();

        adsPlaySingleTtm(args[0]);

        soundEnd();
        graphicsEnd();
    }

    else if (argAds) {

        graphicsInit();

        if (argMinimize)
            minimizeConsoleWindow();

        soundInit();

        if (argIsland) {
            storyUpdateIslandFromDateAndTime();
            adsInitIsland();
        }
        else {
            adsNoIsland();
        }

        {
            char *end = NULL;
            long tagLong = strtol(args[1], &end, 10);

            if (end == args[1] || (end && *end != '\0') || tagLong < 0 || tagLong > 0xFFFFL) {
                fatalError("Invalid ADS tag '%s' (expected 0..65535)", args[1]);
            }

            adsPlay(args[0], (uint16)tagLong);
        }

        soundEnd();
        graphicsEnd();
    }

    zipvfs_shutdown();
    return 0;
}
