libs = ['libPhysics',
        'libEG',
        'libEGPythia6',
        'libGeom',
        'libTree',
        'libxml2',
        'liblog4cpp',
        'libGMessenger.so',
        'libGRegistry.so',
        'libGAlgorithm',
        'libGInteraction',
        'libGHEP',
        'libGBase',
        'libGNumerical',
        'libGUtils',
        'libGPDG',
        'libGBaryonResonance',
        'libGEVGCore',
        'libGEVGDrivers',
        'libGNtuple',
        'libGGeo',
        'libGFluxDrivers',
        "libGPDF",
        "libGElFF",
        "libGDecay",
        "libGFragmentation",
        "libGNuclear",
        "libGLlewellynSmith",
        "libGCrossSections",
        "libGCharm",
        "libGElas",
        "libGGiBUU",
        "libGReinSeghal",
        "libGQPM",
        "libGBodekYang",
        "libGEVGModules",
        "libGQEL",
        "libGRES",
        "libGDIS",
        "libGCoh",
        "libGDfrc",
        "libGMEC",
        "libGNuE",
        "libGNuGamma",
        "libGHadronTransp",]

import ROOT
for lib in libs:
    ROOT.gSystem.Load(lib)
