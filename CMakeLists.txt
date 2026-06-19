cmake_minimum_required(VERSION 3.10)
project(jc_reborn C)

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
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Os")
    # --preload-file produces a separate jc_reborn.data file loaded asynchronously
    # at startup. Emscripten waits for preload to complete before calling main(),
    # so the rest of the engine sees the zip mounted at the expected path.
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -sASYNCIFY -sALLOW_MEMORY_GROWTH -sSTANDALONE_WASM=0 -sNO_EXIT_RUNTIME -sFORCE_FILESYSTEM --preload-file ${CMAKE_SOURCE_DIR}/assets/scrantic_data.zip@scrantic_data.zip")
    set(CMAKE_EXECUTABLE_SUFFIX ".js")
    add_definitions(-DPLATFORM_WEB)
elseif(WIN32)
    message(STATUS "Building for Windows")
    set(PLATFORM_SOURCES platform/platform_windows.c)
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

# Set Objective-C compilation for macOS platform file
if(APPLE)
    set_source_files_properties(platform/platform_macos.m PROPERTIES COMPILE_FLAGS "-x objective-c")
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

# Installation
install(TARGETS jc_reborn DESTINATION bin)

# Print build configuration
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "C Compiler: ${CMAKE_C_COMPILER}")
message(STATUS "C Flags: ${CMAKE_C_FLAGS}")
message(STATUS "Platform sources: ${PLATFORM_SOURCES}")
