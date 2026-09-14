/* Portable PNG alpha contract, independent of WIC and any window server. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "png_decoder.h"

/* Valid 5x1 RGBA PNG with a stored DEFLATE block, real CRCs and Adler checksum.
 * Each pixel selects a different alpha path; the shipped HD art has no partial
 * alpha and therefore cannot witness a broken premultiplication operation. */
static const uint8 fixture[] = {
    0x89,0x50,0x4e,0x47,0x0d,0x0a,0x1a,0x0a,0x00,0x00,0x00,0x0d,
    0x49,0x48,0x44,0x52,0x00,0x00,0x00,0x05,0x00,0x00,0x00,0x01,
    0x08,0x06,0x00,0x00,0x00,0x16,0xfe,0x64,0xf3,0x00,0x00,0x00,
    0x20,0x49,0x44,0x41,0x54,0x78,0x01,0x01,0x15,0x00,0xea,0xff,
    0x00,0x11,0x22,0x33,0xff,0xfa,0x64,0x32,0x00,0xc8,0x64,0x32,
    0x80,0xff,0x00,0xff,0x40,0xa8,0x00,0xa8,0xff,0x58,0xed,0x09,
    0x61,0x51,0x30,0xc4,0x9c,0x00,0x00,0x00,0x00,0x49,0x45,0x4e,
    0x44,0xae,0x42,0x60,0x82
};

int main(void)
{
    static const uint8 expected[][4] = {
        {51,34,17,255}, {0,0,0,0}, {25,50,100,128}, {64,0,64,64}, {168,0,168,255}
    };
    static const char *names[] = {
        "opaque RGB order", "transparent RGB cleared", "half alpha premultiplied",
        "quarter alpha premultiplied", "opaque magenta preserved"
    };
    int width = 0, height = 0, failures = 0;
    uint8 *pixels;

    puts("WITNESS portable PNG decoder executed");
    pixels = pngDecodeToBGRA(fixture, sizeof(fixture), &width, &height);
    if (!pixels || width != 5 || height != 1) {
        fprintf(stderr, "FAIL platform/png_decoder.c: valid RGBA fixture did not decode to 5x1\n");
        free(pixels);
        return 1;
    }
    for (size_t i = 0; i < sizeof(expected) / sizeof(expected[0]); ++i) {
        if (memcmp(pixels + i * 4, expected[i], 4)) {
            fprintf(stderr, "FAIL platform/png_decoder.c: %s, got BGRA %u,%u,%u,%u\n",
                    names[i], (unsigned)pixels[i * 4], (unsigned)pixels[i * 4 + 1],
                    (unsigned)pixels[i * 4 + 2], (unsigned)pixels[i * 4 + 3]);
            failures++;
        }
        else {
            printf("ok   %s\n", names[i]);
        }
    }
    free(pixels);
    return failures ? 1 : 0;
}
