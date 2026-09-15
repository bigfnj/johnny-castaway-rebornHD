#include <errno.h>
#include "/src/src/engine/dump.c"

int __real_fclose(FILE *stream);
int __wrap_fclose(FILE *stream) {
    int result = __real_fclose(stream);
    int saved = errno;
    fprintf(stderr, "WITNESS dump fclose result=%d errno=%d\n", result, saved);
    return result;
}
int main(void) {
    uint16 width = 2, height = 1;
    uint8 data = 0x12;
    struct TBmpResource bmp = {0};
    struct TPalResource palette = {0};
    bmp.resName = "PROBE.BMP";
    bmp.numImages = 1;
    bmp.widths = &width;
    bmp.heights = &height;
    bmp.uncompressedSize = 1;
    bmp.uncompressedData = &data;
    dumpBmp(&bmp, &palette);
    puts("WITNESS dumpBmp returned normally");
    return 0;
}
