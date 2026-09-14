cmake_minimum_required(VERSION 3.10)

# ── Version, single source of truth ───────────────────────────────────────────
# Releases are cut from git tags (v0.9.0, v1.0.0, ...) and .github/workflows/
# release.yml REFUSES to publish when the tag and this number disagree, so the
# two cannot drift. `jc_reborn version` prints this, which it previously could
# not: it said "Development version" and the project carried no version at all.
#
# 1.0.0, 2026-09-14. What kept this below 1.0 was macOS being built and tested
# nowhere; it now builds on macos-latest in CI and its decode output is
# byte-identical to the Windows golden corpus, all 2,452 files. The screensaver
# is complete: /s, /c and /p, verified by registering it in Windows and selecting
# it, plus the input rules a screensaver is expected to honour.
#
# macOS rendering was confirmed by hand on Sequoia, 2026-09-14: right way up,
# correct colours. The audit's upside-down prediction was wrong. Audio, input and
# fullscreen there are still unexercised, so releases ship no macOS artifact yet.
#
# LINUX is now the only platform where nobody has looked at a rendered frame. The
# cross-platform check runs `dump`, which opens no window, so its blitting code
# compiles on every push and is never executed. See BACKLOG.md.
project(jc_reborn VERSION 1.0.0 LANGUAGES C)

set(JC_VERSION_STRING "${PROJECT_VERSION}")

# Set C standard
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

# Compiler flags from original Makefile
if(NOT MSVC)
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wall -Wpedantic -Wextra -Wshadow")
else()
    # MSVC: /W4 is close to -Wall -Wextra
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} /W4")
endif()

# ── Source tree layout ────────────────────────────────────────────────────────
#   src/engine/       — engine core (VMs, graphics, sound, story, I/O plumbing)
#   src/data/         — static data tables baked in as C headers
#   platform/         — platform abstraction + HD I/O adapters (zipvfs, png)
#   third_party/miniz — vendored zip/deflate (miniz by Rich Geldreich)
#   assets/           — runtime data bundle embedded into the web build
#   cmake/            — cross-compilation toolchain files
#   scripts/          — local developer convenience scripts
#   tools/            — standalone helpers (extract_sound, extract_walk_data)
#   vs/               — Visual Studio project files (hand-maintained)
#   docs/             — AI_UNDERSTANDING.md, CHANGELOG.md, HD_README.md

set(COMMON_SOURCES
    # Engine core
    src/engine/jc_reborn.c
    src/engine/utils.c
    src/engine/uncompress.c
    src/engine/resource.c
    src/engine/dump.c
    src/engine/story.c
    src/engine/walk.c
    src/engine/calcpath.c
    src/engine/ads.c
    src/engine/ttm.c
    src/engine/island.c
    src/engine/bench.c
    src/engine/graphics.c
    src/engine/sound.c
    src/engine/events.c
    src/engine/config.c
    # Platform-agnostic I/O adapters
    platform/png_loader.c
    platform/png_decoder.c
    platform/zipvfs.c
    # Vendored zip/deflate
    third_party/miniz/miniz.c
    third_party/miniz/miniz_tdef.c
    third_party/miniz/miniz_tinfl.c
    third_party/miniz/miniz_zip.c
)

# Platform detection and specific sources
if(EMSCRIPTEN)
    message(STATUS "Building for Web (Emscripten)")
    set(PLATFORM_SOURCES platform/platform_web.c)
    # NO -Os HERE. It used to be appended to CMAKE_C_FLAGS, and scripts/build_web.ps1
    # configures with CMAKE_BUILD_TYPE=Release, so CMake appended -O3 from
    # CMAKE_C_FLAGS_RELEASE *after* it. The compile line ended "... -Os ... -O3"
    # and the last flag won, so the size intent recorded in the changelog was
    # silently not happening. Compile optimization is left to the build type.
    # --preload-file produces a separate jc_reborn.data file loaded asynchronously
    # at startup. Emscripten waits for preload to complete before calling main(),
    # so the rest of the engine sees the zip mounted at the expected path.
    # -O2 ON THE LINK LINE, which is where it actually matters here. emcc does its
    # wasm-opt pass and the ASYNCIFY stack-unwinding instrumentation at LINK time,
    # and no optimization flag reached the linker at all - so an ASYNCIFY build,
    # the case that suffers most from it, was being linked at -O0.
    #
    # -sEXPORTED_RUNTIME_METHODS=callMain lets the page pass argv (see index.html),
    # which is what makes `frames`, `seed` and `nosound` reachable in a browser and
    # therefore what makes the web target testable at all.
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -O2 -sASYNCIFY -sALLOW_MEMORY_GROWTH -sSTANDALONE_WASM=0 -sNO_EXIT_RUNTIME -sFORCE_FILESYSTEM -sEXPORTED_RUNTIME_METHODS=callMain,ccall,cwrap --preload-file ${CMAKE_SOURCE_DIR}/assets/scrantic_data.zip@scrantic_data.zip")
    set(CMAKE_EXECUTABLE_SUFFIX ".js")
    add_definitions(-DPLATFORM_WEB)
elseif(WIN32)
    message(STATUS "Building for Windows")
    # THE .rc IS PART OF THE BUILD. CMake never enabled the RC language or listed
    # the resource script, so the CMake-built executable carried no icon at all
    # while the Visual Studio build carried one: same sources, two different
    # products. Combined with a window class that never set hIcon, the result was
    # the blank default box in the title bar, taskbar and Alt-Tab.
    enable_language(RC)
    set(PLATFORM_SOURCES platform/platform_windows.c vs/jc_reborn/jc_reborn.rc)
    add_definitions(-DPLATFORM_WINDOWS)
    # MSVC: quiet down some legacy-C warnings surfaced by /W4 on this codebase
    if(MSVC)
        add_definitions(-D_CRT_SECURE_NO_WARNINGS -DNOMINMAX)
    endif()
    # Static linking for MinGW cross-compilation
    if(CMAKE_CROSSCOMPILING)
        set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -static-libgcc")
    endif()
    # Windows-specific libraries will be added below
elseif(APPLE)
    message(STATUS "Building for macOS")
    set(PLATFORM_SOURCES platform/platform_macos.m)
    add_definitions(-DPLATFORM_MACOS)
    # macOS-specific frameworks will be added below
elseif(UNIX)
    message(STATUS "Building for Linux")
    set(PLATFORM_SOURCES platform/platform_linux.c)
    add_definitions(-DPLATFORM_LINUX)
    # Linux-specific libraries will be added below
else()
    message(FATAL_ERROR "Unsupported platform")
endif()

# Create executable
add_executable(jc_reborn ${COMMON_SOURCES} ${PLATFORM_SOURCES})

# ── Runtime data ──────────────────────────────────────────────────────────────
# The engine opens scrantic_data.zip beside the executable (see zipvfs_init).
# Without this copy the binary builds successfully and then dies on startup,
# which is exactly what it did: the archive lives in assets/ and nothing ever
# put it where the program looks. Emscripten is excluded because --preload-file
# already bakes the archive into jc_reborn.data.
if(NOT EMSCRIPTEN)
    add_custom_command(TARGET jc_reborn POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
                "${CMAKE_SOURCE_DIR}/assets/scrantic_data.zip"
                "$<TARGET_FILE_DIR:jc_reborn>/scrantic_data.zip"
        COMMENT "Copying scrantic_data.zip next to jc_reborn")
endif()

# Set Objective-C compilation for macOS platform file
if(APPLE)
    set_source_files_properties(platform/platform_macos.m PROPERTIES COMPILE_FLAGS "-x objective-c")
endif()

# The version reaches the binary as a define rather than a generated header, so
# there is nothing to regenerate, nothing to gitignore, and no chance of a stale
# copy being compiled. JC_VERSION is quoted here so the C side needs no stringify
# dance.
target_compile_definitions(jc_reborn PRIVATE JC_VERSION="${JC_VERSION_STRING}")

# The SAME version, reaching jc_reborn.rc as three integers so VERSIONINFO's
# FILEVERSION can use them. FILEVERSION needs comma-separated numbers, not a
# string, and the .rc builds its display strings back out of these by
# stringification - which keeps the version in ONE place. Typing it into the .rc
# instead would put it in three: CMakeLists.txt, the .rc, and the git tag that
# release.yml checks against CMakeLists.txt.
if(WIN32 AND NOT EMSCRIPTEN)
    set(JC_RC_DEFS
        JC_VER_MAJOR=${PROJECT_VERSION_MAJOR}
        JC_VER_MINOR=${PROJECT_VERSION_MINOR}
        JC_VER_PATCH=${PROJECT_VERSION_PATCH})
    target_compile_definitions(jc_reborn PRIVATE ${JC_RC_DEFS})
endif()

# Include directories — one entry per source family so #include "foo.h" works
# regardless of which subdir the including .c lives in.
target_include_directories(jc_reborn PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src/engine
    ${CMAKE_CURRENT_SOURCE_DIR}/src/data
    ${CMAKE_CURRENT_SOURCE_DIR}/platform
    ${CMAKE_CURRENT_SOURCE_DIR}/third_party/miniz
)

# Platform-specific linking
if(EMSCRIPTEN)
    # No additional libraries needed for Emscripten
    # Everything is handled through JavaScript
elseif(WIN32)
    # Windows libraries
    target_link_libraries(jc_reborn
        gdi32
        user32
        winmm
        windowscodecs
        ole32
        uuid
    )
elseif(APPLE)
    # macOS frameworks
    find_library(COCOA_FRAMEWORK Cocoa REQUIRED)
    find_library(AUDIO_TOOLBOX AudioToolbox REQUIRED)
    target_link_libraries(jc_reborn
        ${COCOA_FRAMEWORK}
        ${AUDIO_TOOLBOX}
    )
elseif(UNIX)
    # Linux libraries
    find_package(X11 REQUIRED)
    find_package(ALSA REQUIRED)
    find_package(Threads REQUIRED)

    target_include_directories(jc_reborn PRIVATE
        ${X11_INCLUDE_DIR}
        ${ALSA_INCLUDE_DIRS}
    )

    target_link_libraries(jc_reborn
        ${X11_LIBRARIES}
        ${ALSA_LIBRARIES}
        ${CMAKE_THREAD_LIBS_INIT}
        m
    )
endif()

# ── The Windows screensaver ───────────────────────────────────────────────────
# A SECOND TARGET rather than a renamed first one. Windows needs a .scr that is
# a WINDOWS-subsystem binary, because a console-subsystem screensaver flashes a
# console window every time it starts - which is the whole reason the engine
# grew a `minimize` option and a minimizeConsoleWindow() hack. But the console
# build is what every test, `dump` and `help` depends on, so both are kept.
#
# Same sources, same objects, two link results.
if(WIN32 AND NOT EMSCRIPTEN)
    add_executable(jc_reborn_scr WIN32 ${COMMON_SOURCES} ${PLATFORM_SOURCES})

    # JC_IS_SCR lets the shared .rc describe itself correctly. Both targets
    # compile the same resource script, so without it the screensaver would
    # report OriginalFilename "jc_reborn.exe" in its properties dialog.
    target_compile_definitions(jc_reborn_scr PRIVATE
        JC_VERSION="${JC_VERSION_STRING}" ${JC_RC_DEFS} JC_IS_SCR=1)
    target_include_directories(jc_reborn_scr PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/src/engine
        ${CMAKE_CURRENT_SOURCE_DIR}/src/data
        ${CMAKE_CURRENT_SOURCE_DIR}/platform
        ${CMAKE_CURRENT_SOURCE_DIR}/third_party/miniz
    )
    target_link_libraries(jc_reborn_scr gdi32 user32 winmm windowscodecs ole32 uuid comctl32)

    # Windows subsystem with a plain main(). WIN32 above asks the linker for
    # /SUBSYSTEM:WINDOWS, which normally demands WinMain; pointing the entry at
    # mainCRTStartup keeps the existing main(argc, argv) and the real argv the
    # shell passes in /p and /c:<hwnd>. The alternative - a WinMain that
    # re-parses GetCommandLine() - would duplicate quoting rules for no gain.
    if(MSVC)
        set_target_properties(jc_reborn_scr PROPERTIES LINK_FLAGS "/ENTRY:mainCRTStartup")
    endif()

    # .scr IS the deliverable: Windows only lists files with this extension in
    # the Screen Saver dropdown.
    set_target_properties(jc_reborn_scr PROPERTIES
        OUTPUT_NAME "jc_reborn"
        SUFFIX ".scr")

    # The archive has to travel with it, exactly as for the console build: an
    # installed .scr runs from System32 and finds its data beside itself.
    add_custom_command(TARGET jc_reborn_scr POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
                "${CMAKE_SOURCE_DIR}/assets/scrantic_data.zip"
                "$<TARGET_FILE_DIR:jc_reborn_scr>/scrantic_data.zip"
        COMMENT "Copying scrantic_data.zip next to jc_reborn.scr")
endif()

# Installation
# The archive is installed alongside the binary for the same reason it is copied
# post-build: the engine cannot start without it, so a bin/ holding only the
# executable is not a working install.
install(TARGETS jc_reborn DESTINATION bin)
if(NOT EMSCRIPTEN)
    install(FILES "${CMAKE_SOURCE_DIR}/assets/scrantic_data.zip" DESTINATION bin)
endif()

# Print build configuration
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "C Compiler: ${CMAKE_C_COMPILER}")
message(STATUS "C Flags: ${CMAKE_C_FLAGS}")
message(STATUS "Platform sources: ${PLATFORM_SOURCES}")
