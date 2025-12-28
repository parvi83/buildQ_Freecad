set(Namespace_SRCS
        freecad/buildQ_module/init_gui.py
        freecad/buildQ_module/__init__.py
        freecad/buildQ_module/my_numpy_function.py
        freecad/buildQ_module/version.py
        freecad/buildQ_module/resources/cool.svg
        freecad/buildQ_module/resources/translations/buildQ_module_es-ES.qm
        freecad/buildQ_module/resources/translations/buildQ_module_es-ES.ts
)

SOURCE_GROUP("" FILES ${Namespace_SRCS})

ADD_CUSTOM_TARGET(SEARCHBAR ALL
        SOURCES ${Namespace_SRCS}
)

fc_copy_sources(SEARCHBAR "${CMAKE_BINARY_DIR}/Mod/buildQ_Freecad" ${Namespace_SRCS})

INSTALL(
    FILES
        ${Namespace_SRCS}
    DESTINATION
        Mod/SearchBar
)
