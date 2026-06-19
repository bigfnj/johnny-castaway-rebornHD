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

#include "platform.h"
#include <stdio.h>
#include <string.h>

#include "mytypes.h"
#include "utils.h"
#include "sound.h"
#include "zipvfs.h"


#define NUM_OF_SOUNDS  25


struct TSound {
    uint32  length;
    uint8   *data;
};


int soundDisabled = 0;


static struct TSound sounds[NUM_OF_SOUNDS];
static struct TSound *currentSound;

static uint8  *currentPtr;
static uint32 currentRemaining;


static void soundCallback(void *userdata, uint8 *stream, int rqdLen)
{
    (void)userdata;

    if (rqdLen <= 0) {
        return;
    }

    platformLockAudio();

    if (currentRemaining > (uint32)rqdLen) {
        memcpy(stream, currentPtr, (size_t)rqdLen);
        currentPtr += rqdLen;
        currentRemaining -= (uint32)rqdLen;
    }
    else {
        int remaining = (int)currentRemaining;
        memcpy(stream, currentPtr, (size_t)remaining);
        memset(stream + remaining, 128, (size_t)(rqdLen - remaining));  // 128 == silence for 8-bit unsigned PCM
        currentRemaining = 0;
    }

    platformUnlockAudio();
}


void soundInit(void)
{
    if (soundDisabled)
        return;

    if (platformInitAudio() < 0) {
        debugMsg("Platform init audio error: %s", platformGetError());
        soundDisabled = 1;
        return;
    }

    PlatformAudioSpec audioSpec = {0};
    int haveSpec = 0;

    for (int i=1; i < NUM_OF_SOUNDS; i++) {

        char filename[20];
        snprintf(filename, sizeof(filename), "data/sound%d.wav", i);

        size_t wavSize = 0;
        uint8 *wavData = zipvfs_read(filename, &wavSize);

        if (wavData) {
            PlatformAudioSpec wavSpec;
            if (platformLoadWAVFromMemory(wavData, (uint32)wavSize, &wavSpec,
                                          &sounds[i].data, &sounds[i].length) != 0) {
                sounds[i].data   = NULL;
                sounds[i].length = 0;
                debugMsg("platformLoadWAVFromMemory() warning: %s", platformGetError());
            }
            else {
                if (!haveSpec) {
                    audioSpec = wavSpec;
                    haveSpec = 1;
                }
                else if (wavSpec.freq != audioSpec.freq || wavSpec.channels != audioSpec.channels) {
                    debugMsg("Warning: sound%d.wav has different format (freq=%d ch=%d vs freq=%d ch=%d)",
                             i, wavSpec.freq, wavSpec.channels, audioSpec.freq, audioSpec.channels);
                }
            }
            free(wavData);
        }
        else {
            sounds[i].data   = NULL;
            sounds[i].length = 0;
            debugMsg("WAV file not found in zip: %s", filename);
        }
    }

    if (!haveSpec) {
        debugMsg("No WAV files loaded, disabling sound");
        soundDisabled = 1;
        return;
    }

    audioSpec.callback = soundCallback;
    audioSpec.userdata = NULL;
    audioSpec.samples  = 1024;

    if (platformOpenAudio(&audioSpec) < 0) {
        debugMsg("platformOpenAudio() error: %s", platformGetError());
        soundDisabled = 1;
        return;
    }

    currentRemaining = 0;
    platformPauseAudio(0);
}


void soundEnd(void)
{
    if (soundDisabled)
        return;

    platformCloseAudio();

    for (int i=0; i < NUM_OF_SOUNDS; i++)
        if (sounds[i].data != NULL)
            platformFreeWAV(sounds[i].data);
}


void soundPlay(int nb)
{
    if (soundDisabled)
        return;

    if (nb < 0 || NUM_OF_SOUNDS <= nb) {
        debugMsg("soundPlay(): wrong sound sample index #%d", nb);
        return;
    }

    if (sounds[nb].length) {

        platformLockAudio();

        currentSound     = &sounds[nb];
        currentPtr       = currentSound->data;
        currentRemaining = currentSound->length;

        platformUnlockAudio();
    }
    else {
        debugMsg("Non-existent sound sample #%d", nb);
    }
}

