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
#include <stdarg.h>
#include <time.h>

#include "mytypes.h"
#include "utils.h"


#define BUF_LEN 256

static struct tm* localtime_safe(const time_t* t, struct tm* out)
{
#if defined(_WIN32)
    return (localtime_s(out, t) == 0) ? out : NULL;
#elif defined(__unix__) || defined(__APPLE__)
    {
        if (localtime_r(t, out) == NULL)
            return NULL;
        return out;
    }
#else
    (void)out;
    return localtime(t);
#endif
}

int debugMode = 0;

JCR_NORETURN void fatalError(const char *message, ... )
{
    va_list(args);

    va_start(args, message);
    fprintf(stderr, "\n\n Fatal error : ");
    vfprintf(stderr, message, args);
    fprintf(stderr, "\n\n");
    va_end(args);

    exit(1);
}


void debugMsg(const char *message, ... )
{
    if (debugMode) {
        va_list(args);
        va_start(args, message);
        vprintf(message, args);
        printf("\n");
        va_end(args);
    }
}


void *safe_malloc(size_t size)
{
    void *ptr = malloc(size);

    if (ptr == NULL)
        fatalError("failed to malloc() %zu bytes", size);

    return ptr;
}


FILE *safe_fopen(const char *pathname, const char *mode)
{
    FILE *f;

    f = fopen(pathname, mode);

    if (f == NULL)
        fatalError("unable to open file %s in mode '%s'", pathname, mode);

    return f;
}


static uint8 readByteOrDie(FILE *f)
{
    int c = fgetc(f);
    if (c == EOF)
        fatalError("Unexpected end of file while reading binary data");
    return (uint8)c;
}


uint8 readUint8(FILE *f)
{
    return readByteOrDie(f);
}


uint16 readUint16(FILE *f)
{
    uint16 a;

    a  = (uint16)readByteOrDie(f);
    a |= (uint16)((uint16)readByteOrDie(f) << 8);

    return a;
}


uint32 readUint32(FILE *f)
{
    uint32 a;

    a  = (uint32)readByteOrDie(f);
    a |= (uint32)readByteOrDie(f) << 8;
    a |= (uint32)readByteOrDie(f) << 16;
    a |= (uint32)readByteOrDie(f) << 24;

    return a;
}


char *getString(FILE *f, int maxlen)
{
    int numread = 0;
    int lastread = 1;
    char buf[BUF_LEN];
    char *out;

    while ((numread < maxlen) && (numread < BUF_LEN) && (lastread != 0)) {

        uint8 b = readByteOrDie(f);
        lastread = (int)b;
        buf[numread++] = (char)b;
    }

    // Ensure null-termination: if the data didn't end with '\0', add one
    int allocSize = numread;
    if (numread == 0 || buf[numread - 1] != '\0')
        allocSize = numread + 1;

    out = safe_malloc((size_t)allocSize * sizeof(char));
    memcpy(out, buf, (size_t)numread);
    out[allocSize - 1] = '\0';
    return out;
}


uint8 *readUint8Block(FILE *f, int len)
{
    uint8 *out = safe_malloc((size_t)len * sizeof(uint8));

    for (int i=0; i < len; i++)
        out[i] = readByteOrDie(f);

    return out;
}


uint16 *readUint16Block(FILE *f, int len)
{
    uint16 *out = safe_malloc((size_t)len * sizeof(uint16));

    for (int i=0; i < len; i++)
        out[i] = readUint16(f);

    return out;
}


uint16 peekUint16(uint8 *data, uint32 *offset)
{
    uint16 result;

    result  = data[(*offset)++];
    result |= (uint16)((uint16)data[(*offset)++] << 8);

    return result;
}


void peekUint16Block(uint8 *data, uint32 *offset, uint16 *dest, int len)
{
    for (int i=0; i < len ; i++)
        dest[i] = peekUint16(data, offset);
}


void hexdump(uint8 *data, uint32 len)
{
    if (data==NULL)
    {
        printf("Can't dump NULL data\n");
        return;
    }

    printf("\n");

    for (uint32 i=0; i < len; i++) {

        printf("%02x ",data[i]);

        if ((i & 0x0f) == 0x07) { printf (" ");  }
        if ((i & 0x0f) == 0x0f) { printf ("\n"); }
    }

    printf("\n");
}


int getDayOfYear(void)
{
    time_t t = time(NULL);
    struct tm tm_buf;
    struct tm *localTime = localtime_safe(&t, &tm_buf);

    return localTime ? localTime->tm_yday : 0;
}



int getHour(void)
{
    time_t t = time(NULL);
    struct tm tm_buf;
    struct tm *localTime = localtime_safe(&t, &tm_buf);

    return localTime ? localTime->tm_hour : 0;
}



char *getMonthAndDay(void)
{
    time_t t = time(NULL);
    struct tm tm_buf;
    struct tm *localTime = localtime_safe(&t, &tm_buf);
    static char result[5] = "0000";

    if (localTime) {
        strftime(result, sizeof(result), "%m%d", localTime);
    }

    return result;
}


