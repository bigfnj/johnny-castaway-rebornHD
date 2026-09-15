# Keep the data beside each native executable without forcing C compilation or
# linking after an artwork-only change. Requires CMP0112 NEW (CMake 3.19).
function(jc_add_runtime_data archive)
    set(copy_commands)
    foreach(runtime_target IN LISTS ARGN)
        list(APPEND copy_commands
            COMMAND "${CMAKE_COMMAND}" -E make_directory "$<TARGET_FILE_DIR:${runtime_target}>"
            COMMAND "${CMAKE_COMMAND}" -E copy_if_different
                    "${archive}" "$<TARGET_FILE_DIR:${runtime_target}>/scrantic_data.zip")
    endforeach()
    add_custom_target(jc_runtime_data ALL
        ${copy_commands}
        DEPENDS "${archive}"
        COMMENT "Refreshing runtime artwork archive"
        VERBATIM)
    foreach(runtime_target IN LISTS ARGN)
        add_dependencies(${runtime_target} jc_runtime_data)
    endforeach()
endfunction()
