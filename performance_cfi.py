import FWCore.ParameterSet.Config as cms

performance = cms.EDAnalyzer('Performance',
                             caloParticles      = cms.InputTag("mix"                , "MergedCaloTruth"),
                             hgcalRecHitsEE     = cms.InputTag("HGCalRecHit"        , "HGCEERecHits"),
                             hgcalRecHitsFH     = cms.InputTag("HGCalRecHit"        , "HGCHEFRecHits"),
                             hgcalRecHitsBH     = cms.InputTag("HGCalRecHit"        , "HGCHEBRecHits"),
                             hgcalLayerClusters = cms.InputTag("hgcalLayerClusters" , ""                 , "RECO"),
                             layerClusterTime   = cms.InputTag("hgcalLayerClusters" , "timeLayerCluster" , "RECO"),
                             emTrkster          = cms.InputTag("trackstersEM"       , ""                 , "RECO" ),
                             hadTrkster         = cms.InputTag("trackstersHAD"      , ""                 , "RECO" ),
                             mipTrkster         = cms.InputTag("trackstersMIP"      , ""                 , "RECO" ),
                             trkTrkster         = cms.InputTag("trackstersTrk"      , ""                 , "RECO" ),
                             mergeTrkster       = cms.InputTag("trackstersMerge"    , ""                 , "RECO" ),
                         )
