import sys
makeTrees = sys.argv[1].lower() == 'true'
makePlots = sys.argv[2].lower() == 'true'
pid_str = sys.argv[3]
nameprefix = sys.argv[4]

print("Running with option makeTrees = {}, makePlots = {}, particleId = {}, condition = {}".format(makeTrees, makePlots, pid_str, nameprefix))
import os, subprocess
import  ROOT

if not os.path.exists(outPath):
    os.mkdir(outPath)

treeName = "performance/tree"
deltaBary_lim = 0.1 
deltaAxis_lim = 0.5
histTitles = {"BaryCP": {"name": "Trackster barycenter - CaloParticle", "lim": deltaBary_lim, "branch": "EBary_cp0"}, "AxisCP": {"name": "Trackster axis - CaloParticle", "lim": deltaAxis_lim, "branch": "EAxis_cp0"}}
histVars = {"DEta": "#Delta#eta", "DPhi": "#Delta#phi"}

for E in [10, 100]:
  outPath = "/eos/user/l/lecriste/HGCal/www"
  outPath = os.path.join(outPath,pid_str)
  inputPath = outPath
  outPath = os.path.join(outPath, str(E)+"GeV")
  if not os.path.exists(outPath):
    os.mkdir(outPath)

  for r in range(25, 160, 5):
    if makeTrees:
      bashCommand = "cmsRun run_performance_cfg.py {} {} {} {}".format(pid_str, E, nameprefix, r)
      process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
      output, error = process.communicate()

    if makePlots:
      inputFile_ = "file:"+inputPath+"/hgc_perftree_e{}GeV_r{}_{}.root".format(E, r, nameprefix)
      print("\nOpening file {}".format(inputFile_))
      if not inputFile_:
        print("No such file")
        continue
      inFile = ROOT.TFile.Open(inputFile_,"READ")
      tree = inFile.Get(treeName)
      if not tree:
        print("No {} found in file\n{}".format(treeName, inputFile_))
        continue

      # TH1
      for name, title in histTitles.items():
        for varName, varLabel in histVars.items():
          hist = ROOT.TH1F("{}_{}".format(name,varName),"{};{}".format(title['name'],varLabel) , 100,-title['lim'],title['lim'])
          branchName = "{}_{}".format(title['branch'], "eta" if "eta" in varLabel else "phi")
          canvas = ROOT.TCanvas("canvas_"+branchName)
          canvas.cd()

          for entryNum in range(0, tree.GetEntries()):
            tree.GetEntry(entryNum)
            var = getattr(tree, branchName)
            hist.Fill(var)

          hist.Draw("h")
          canvas.Print(outPath+"/"+branchName+"_r"+str(r)+".png")

      # TH2
      for varName, varLabel in histVars.items():
        hist = ROOT.TH1F("Axis-Barycenter","{varLabel};{varLabel};", 100,-title['lim'],title['lim'],100,-title['lim'],title['lim'])
        for name, title in histTitles.items():
          for entryNum in range(0, tree.GetEntries()):
            tree.GetEntry(entryNum)
            var[name] = getattr(tree, branchName)

          hist.Fill(var[],var[])

      inFile.Close()
