/*
 *  Zip Virtual Filesystem for Johnny Reborn
 *
 *  Provides transparent read access to game assets stored inside a zip archive.
 *  Uses miniz for zip decompression.
 */

#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "miniz.h"
#include "miniz_zip.h"
#include "mytypes.h"
#include "utils.h"
#include "zipvfs.h"


static mz_zip_archive g_zip;
static int g_zipInitialized = 0;


void zipvfs_init(const char *zipPath)
{
    if (g_zipInitialized) {
        debugMsg("zipvfs_init: already initialized, shutting down first");
        zipvfs_shutdown();
    }

    memset(&g_zip, 0, sizeof(g_zip));

    if (!mz_zip_reader_init_file(&g_zip, zipPath, 0)) {
        fatalError("Failed to open zip archive: %s\n"
                   "Please ensure scrantic_data.zip is in the same directory as the executable.",
                   zipPath);
    }

    g_zipInitialized = 1;

    debugMsg("zipvfs: opened archive '%s' (%u entries)",
             zipPath, (unsigned)mz_zip_reader_get_num_files(&g_zip));
}


FILE *zipvfs_fopen(const char *entryPath)
{
    if (!g_zipInitialized)
        fatalError("zipvfs_fopen: zip VFS not initialized");

    int index = mz_zip_reader_locate_file(&g_zip, entryPath, NULL, 0);
    if (index < 0)
        return NULL;

    mz_zip_archive_file_stat stat;
    if (!mz_zip_reader_file_stat(&g_zip, (mz_uint)index, &stat))
        return NULL;

    size_t size = (size_t)stat.m_uncomp_size;
    void *data = mz_zip_reader_extract_to_heap(&g_zip, (mz_uint)index, &size, 0);
    if (!data)
        return NULL;

    /* Create a temporary file and write the decompressed data into it.
     * This gives us a real seekable FILE* that the existing resource
     * parsing code can use without any changes. */
    FILE *f = NULL;
#if defined(_WIN32)
    {
        // On Windows, tmpfile() may fail without admin privileges
        // and doesn't guarantee binary mode. Use _tempnam + fopen instead.
        char *tmpPath = _tempnam(NULL, "jcr");
        if (tmpPath) {
            f = fopen(tmpPath, "w+bTD");  // T=short-lived, D=delete-on-close
            free(tmpPath);
        }
    }
#else
    f = tmpfile();
#endif
    if (!f) {
        free(data);
        fatalError("zipvfs_fopen: tmpfile() failed");
    }

    if (fwrite(data, 1, size, f) != size) {
        free(data);
        fclose(f);
        fatalError("zipvfs_fopen: failed to write to temp file");
    }

    free(data);
    rewind(f);
    return f;
}


uint8 *zipvfs_read(const char *entryPath, size_t *outSize)
{
    if (!g_zipInitialized)
        fatalError("zipvfs_read: zip VFS not initialized");

    int index = mz_zip_reader_locate_file(&g_zip, entryPath, NULL, 0);
    if (index < 0)
        return NULL;

    size_t size = 0;
    void *data = mz_zip_reader_extract_to_heap(&g_zip, (mz_uint)index, &size, 0);
    if (!data)
        return NULL;

    if (outSize)
        *outSize = size;

    return (uint8 *)data;
}


int zipvfs_exists(const char *entryPath)
{
    if (!g_zipInitialized)
        return 0;

    return mz_zip_reader_locate_file(&g_zip, entryPath, NULL, 0) >= 0;
}


void zipvfs_shutdown(void)
{
    if (g_zipInitialized) {
        mz_zip_reader_end(&g_zip);
        g_zipInitialized = 0;
    }
}
