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
#define TOOL "tools/extract_sound.c"

static const long offsets[] = {
    0x1DC00, 0x20800, 0x20E00,
    0x22C00, 0x24000, 0x24C00,
    0x28A00, 0x2C600, 0x2D000,
    0x2DE00, 0x34400, 0x32E00,
    0x39C00, 0x43400, 0x37200,
    0x37E00, 0x45A00, 0x3AE00,
    0x3E600, 0x3F400, 0x41200,
    0x42600, 0x42C00, 0x43400
};

int main(int argc, char **argv)
{
    const char *input = NULL, *directory = NULL, *layout = NULL;
    unsigned char *buffers[24] = {0};
    size_t sizes[24] = {0};
    char *paths[24] = {0};
    FILE *outputs[24] = {0}, *file = NULL;
    int created[24] = {0};
    long file_size = 0;
    int result = 1;
    for (int i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--help") == 0 && argc == 2) {
            puts("Usage: extract_sound --layout legacy-fixed-offsets --input FILE --output-dir EXISTING_DIRECTORY\n"
                 "Preserves legacy sound1..24 names, fixed offsets and first-u16-plus-8 lengths.\n"
                 "This layout is not RIFF parsing; original SCRANTIC.SCR parity is unverified. Existing outputs are preserved.");
            return 0;
        }
        if (i + 1 < argc && strcmp(argv[i], "--input") == 0 && !input) input = argv[++i];
        else if (i + 1 < argc && strcmp(argv[i], "--output-dir") == 0 && !directory) directory = argv[++i];
        else if (i + 1 < argc && strcmp(argv[i], "--layout") == 0 && !layout) layout = argv[++i];
        else { extract_error(TOOL, argv[i], "unknown, repeated or incomplete option (use --help)"); return 1; }
    }
    if (!input || !directory || !layout || strcmp(layout, "legacy-fixed-offsets") != 0) {
        extract_error(TOOL, "arguments", "require --layout legacy-fixed-offsets --input FILE --output-dir DIRECTORY (use --help)");
        return 1;
    }
    fprintf(stderr, "INFO %s: legacy fixed-offset layout; original SCRANTIC.SCR parity is unverified\n", TOOL);
    file = extract_open_input(TOOL, input, &file_size);
    if (!file) goto done;
    /* Read every requested span before creating any output. Do not reinterpret
       these historical lengths as RIFF lengths or remove the duplicate offset. */
    for (int j = 0; j < 24; ++j) {
        unsigned char header[2];
        size_t path_size = strlen(directory) + 32;
        if (!extract_read(TOOL, file, input, file_size, offsets[j], header, sizeof(header))) goto done;
        sizes[j] = (size_t)extract_u16(header) + 8;
        buffers[j] = malloc(sizes[j]);
        paths[j] = malloc(path_size);
        if (!buffers[j] || !paths[j]) { extract_error(TOOL, input, "allocation failed"); goto done; }
        snprintf(paths[j], path_size, "%s/sound%d.wav", directory, j + 1);
        if (!extract_read(TOOL, file, input, file_size, offsets[j], buffers[j], sizes[j])) goto done;
    }
    if (fclose(file) != 0) { file = NULL; extract_error(TOOL, input, "input close failed"); goto done; }
    file = NULL;
    for (int j = 0; j < 24; ++j) {
        outputs[j] = extract_create(TOOL, paths[j]);
        if (!outputs[j]) goto done;
        created[j] = 1;
    }
    for (int j = 0; j < 24; ++j)
        if (!extract_write(TOOL, &outputs[j], paths[j], buffers[j], sizes[j])) goto done;
    result = 0;
    fprintf(stderr, "PASS %s: extracted 24 legacy blocks\n", TOOL);
done:
    if (file) fclose(file);
    for (int j = 0; j < 24; ++j) {
        if (outputs[j]) fclose(outputs[j]);
        if (result != 0 && created[j]) remove(paths[j]);
        free(paths[j]);
        free(buffers[j]);
    }
    return result;
}
