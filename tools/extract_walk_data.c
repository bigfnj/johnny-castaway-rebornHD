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
#include "extract_io.h"
#define TOOL "tools/extract_walk_data.c"
#define WALK_RECORDS 489

int main(int argc, char **argv)
{
    const char *input = NULL, *output = NULL;
    unsigned char bytes[WALK_RECORDS * 6];
    char text[WALK_RECORDS * 64];
    size_t used = 0;
    long size = 0;
    FILE *file;
    for (int i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--help") == 0 && argc == 2) {
            puts("Usage: extract_walk_data --input FILE --output FILE|-\n"
                 "Emits exactly 489 legacy records at 0x188EA; '-' writes the table to stdout.\n"
                 "Original SCRANTIC.SCR parity is unverified. Existing outputs are preserved.");
            return 0;
        }
        if (i + 1 < argc && strcmp(argv[i], "--input") == 0 && !input) input = argv[++i];
        else if (i + 1 < argc && strcmp(argv[i], "--output") == 0 && !output) output = argv[++i];
        else { extract_error(TOOL, argv[i], "unknown, repeated or incomplete option (use --help)"); return 1; }
    }
    if (!input || !output) {
        extract_error(TOOL, "arguments", "require --input FILE --output FILE|- (use --help)");
        return 1;
    }
    fprintf(stderr, "INFO %s: legacy 489-record layout; original SCRANTIC.SCR parity is unverified\n", TOOL);
    file = extract_open_input(TOOL, input, &size);
    if (!file) return 1;
    if (!extract_read(TOOL, file, input, size, 0x188ea, bytes, sizeof(bytes))) { fclose(file); return 1; }
    if (fclose(file) != 0) { extract_error(TOOL, input, "input close failed"); return 1; }
    /* The former ftell-driven inclusive loop emitted 489 records, including
       its last separator. An endpoint divided by six would drop that record. */
    for (int i = 0; i < WALK_RECORDS; ++i) {
        const unsigned char *row = bytes + i * 6;
        unsigned int first = extract_u16(row);
        int length = snprintf(text + used, sizeof(text) - used, "    { %d, %3d, %3d, %2d },\n",
                              (int)(first >> 15), (int)extract_u16(row + 2),
                              (int)extract_u16(row + 4), (int)(first & 0x7fff));
        if (length < 0 || (size_t)length >= sizeof(text) - used) {
            extract_error(TOOL, output, "record formatting failed"); return 1;
        }
        used += (size_t)length;
    }
    if (strcmp(output, "-") == 0) {
        if (fwrite(text, 1, used, stdout) != used || fflush(stdout) != 0) {
            extract_error(TOOL, "stdout", "output write failed"); return 1;
        }
    } else {
        file = extract_create(TOOL, output);
        if (!file) return 1;
        if (!extract_write(TOOL, &file, output, text, used)) { remove(output); return 1; }
    }
    fprintf(stderr, "PASS %s: extracted 489 legacy records\n", TOOL);
    return 0;
}
