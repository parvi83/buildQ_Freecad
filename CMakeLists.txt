set(Namespace_SRCS
        freecad/buildQ/init_gui.py
        freecad/buildQ/__init__.py
        freecad/buildQ/my_numpy_function.py
        freecad/buildQ/version.py
        freecad/buildQ/resources/cool.svg
        freecad/buildQ/resources/translations/buildQ_es-ES.qm
        freecad/buildQ/resources/translations/buildQ_es-ES.ts
)

SOURCE_GROUP("" FILES ${Namespace_SRCS})

ADD_CUSTOM_TARGET(SEARCHBAR ALL
        SOURCES ${Namespace_SRCS}
)

fc_copy_sources(SEARCHBAR "${CMAKE_BINARY_DIR}/Mod/buildQ" ${Namespace_SRCS})

INSTALL(
    FILES
        ${Namespace_SRCS}
    DESTINATION
        Mod/SearchBar
)
