import FWCore.ParameterSet.Config as cms

import FWCore.ParameterSet.Config as cms 
from Configuration.ProcessModifiers.convertHGCalDigisSim_cff import convertHGCalDigisSim

from Configuration.Eras.Era_Phase2_cff import Phase2
#process = cms.Process('DIGI',Phase2,convertHGCalDigisSim)

process = cms.Process("performance")

from Configuration.Eras.Era_Phase2C9_cff import Phase2C9
process = cms.Process('PROD',Phase2C9)
process.load('Configuration.Geometry.GeometryExtended2026D49Reco_cff')

process.load("SimGeneral.HepPDTESSource.pythiapdt_cfi")
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('Configuration.StandardSequences.Services_cff')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:phase2_realistic', '')

import sys
pid_str = sys.argv[2]
en_str = sys.argv[3]
nameprefix = sys.argv[4] 
r_str = sys.argv[5]

import os

#path_ = "/data/hgcal-0/user/gouskos/samples/forCTDots2020/step3_cmssw_11_1_X_2020-02-18-1100/photons_closeby_hgcalcenter/"
#path_ = "/data/hgcal-0/user/gouskos/samples/forCTDots2020_111X/photons_closeby_fixedenergy_scaneta/step3/"
#path_ = "/data2/user/gouskos/samples/forCTDots2020_111X/photons_closeby_fixedenergy_scaneta/step3/"
#path_ = "/data2/user/gouskos/samples/forCTDots2020_111X/photons_closeby_fixedenergy_scaneta/step3_stepSize2/"
path_ = "/data2/user/lecriste/HGCal/samples/111X_PF_Mar9/photons_closeby_fixedenergy_scaneta/step3/"

#inputfile_  = "file:"+path_+"step3_{}_e{}GeV_{}.root".format(pid_str, en_str, nameprefix)
inputfile_  = "file:"+path_+"step3_{}_e{}GeV_r{}_{}.root".format(pid_str, en_str, r_str, nameprefix)
#inputfile_  = "file:step3.root"

#outputfile_ = "file:/data/hgcal-0/user/gouskos/samples/forCTDots2020_111X/trees/photons_closeby_hgcalcenter/hgc_perftree_{}_e{}GeV_{}.root".format(pid_str, en_str, nameprefix)
#outputfile_ = "file:/data2/user/gouskos/samples/forCTDots2020_111X/photons_closeby_fixedenergy_scaneta/trees_stepSize2/hgc_perftree_{}_e{}GeV_r{}_{}.root".format(pid_str, en_str, r_str, nameprefix)
#outPath = "/eos/user/l/lecriste/HGCal/www"
outPath = "/afs/cern.ch/work/l/lecriste/www/HGCAL/"
outPath = os.path.join(outPath,pid_str)
if not os.path.exists(outPath):
    os.mkdir(outPath)
outputfile_ = "file:"+outPath+"/hgc_perftree_e{}GeV_r{}_{}.root".format(en_str, r_str, nameprefix)

print inputfile_ 
print outputfile_

process.MessageLogger.cerr.FwkReport.reportEvery = 50

process.TFileService = cms.Service("TFileService",
                                   fileName = cms.string(outputfile_),
                                   closeFileFast = cms.untracked.bool(True)
                               )

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

process.source = cms.Source(
    "PoolSource",
    fileNames = cms.untracked.vstring([
        inputfile_
        #'file:single_pi_pgun/step3_singlepi_e100GeV.root'
    ]
                                  )
)

#process.load("hgc_analyzer_for_ml.HGCPerformanceAnalyzer.performance_cfi")
process.load("performance_cfi")
process.p = cms.Path(process.performance)
