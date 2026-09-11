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

#include "platform.h"
#include "mytypes.h"
#include "graphics.h"
#include "sound.h"
#include "events.h"


static uint32 lastTicks = 0x00ffffff;
static int paused   = 0;
static int maxSpeed = 0;
static int oneFrame = 0;

int evHotKeysEnabled = 0;

/*  Bounded run, for automated testing. 0 means unlimited, which is the default
 *  and the shipping behaviour: storyPlay() loops forever and only ever leaves
 *  through exit() on an input event. That is correct for a screensaver and
 *  impossible to assert on, because a test can only kill it and guess whether
 *  it was healthy. With `frames N` the engine shuts down cleanly through the
 *  normal path and returns 0, so a smoke test can check an exit code instead.
 */
uint32 evMaxFrames = 0;
static uint32 evFrameCount = 0;

/*  Max speed as a startup option, not just the <M> hotkey. The per-scene delay
 *  floor is 80 ms (12.5 FPS), so covering enough story iterations to exercise
 *  the island setup/teardown cycle takes minutes of wall clock at normal speed.
 *  The hotkey already proved the engine runs correctly unthrottled; this only
 *  makes that reachable without a keyboard.
 */
int evStartAtMaxSpeed = 0;


static void eventsProcessEvents(void)
{
    PlatformEvent event;

    while (platformPollEvent(&event)) {

        switch(event.type) {

            case EVENT_KEY_DOWN:

                if (evHotKeysEnabled) {

                    switch (event.data.key.keycode) {

                        case KEY_SPACE:
                            paused = !paused;
                            break;

                        case KEY_M:
                            maxSpeed = !maxSpeed;
                            break;

                        case KEY_RETURN:
                            if (event.data.key.modifiers & KEYMOD_LALT) {
                                grToggleFullScreen();
                                oneFrame = 1;   // to redraw the window // TODO
                            }
                            else {
                                oneFrame = 1;
                            }
                            break;

                        case KEY_ESCAPE:
                            soundEnd();
                            graphicsEnd();
                            exit(255);
                            break;

                        default:
                            break;
                    }
                }
                else {
                    // Normal behaviour : no hot keys, the screen saver
                    // terminates if any key is pressed
                        soundEnd();
                        graphicsEnd();
                    exit(255);
                }
                break;

            case EVENT_WINDOW_REFRESH:
                grRefreshDisplay();
                break;

            case EVENT_QUIT:
                    soundEnd();
                    graphicsEnd();
                exit(255);
                break;

            default:
                break;
        }
    }
}


void eventsInit(void)
{
    lastTicks = platformGetTicks();
    maxSpeed  = evStartAtMaxSpeed;
    atexit(platformShutdown);
}


void eventsWaitTick(uint16 delay)
{
    /*  WIDENED to 32 bits before the multiply. `delay *= 20` on the uint16
     *  parameter wrapped for any delay above 3276 ticks, so a script asking to
     *  wait 4000 ticks (80 s) slept 14.4 s instead. No shipped script asks for
     *  more than 660, so this has never fired, but the arithmetic was wrong and
     *  the clamp that hides it lives in a different file.
     */
    uint32 delayMs = (uint32)delay * 20u;

    oneFrame = 0;

    /*  Bounded run. Counted here because this is the one function every frame
     *  passes through, whichever mode is playing. Shutdown goes through the
     *  same soundEnd/graphicsEnd path as a user quit, so what the test exercises
     *  is the real teardown, not a shortcut around it. Exit code 0, because
     *  reaching the requested frame count is success; the input-driven quit
     *  paths keep their 255.
     */
    if (evMaxFrames) {
        if (++evFrameCount > evMaxFrames) {
            soundEnd();
            graphicsEnd();
            exit(0);
        }
    }

    eventsProcessEvents();

    while ((paused && !oneFrame)
            || (!maxSpeed && (platformGetTicks() - lastTicks < delayMs))) {
        platformDelay(5);
        eventsProcessEvents();
    }

    lastTicks = platformGetTicks();
}
