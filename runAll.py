import sys
makeTrees = sys.argv[1].lower() == 'true'
makePlots = sys.argv[2].lower() == 'true'
pid_str = sys.argv[3]
nameprefix = sys.argv[4]
step = int(sys.argv[5])

print("Running with option makeTrees = {}, makePlots = {}, particleId = {}, condition = {}, step = {}".format(makeTrees, makePlots, pid_str, nameprefix, step))
import os, subprocess
import  ROOT

#pointing = "Pointing"
pointing = "nonPointing"

treeName = "performance/tree"
sig = 'sig'
deltaBary_lim = 0.1 
binWidthBary = 0.005
deltaAxis_lim = 0.5
binWidthAxis = 0.01

scatter_lim = max(deltaBary_lim,deltaAxis_lim)
binNBary = int(scatter_lim*2/binWidthBary)
binNAxis = int(scatter_lim*2/binWidthAxis)
histTitles = {"Bary-CP": {"name": "Trackster barycenter - CaloParticle", "lim": deltaBary_lim, "branch": "EBary_cp0", "color": ROOT.kRed}, "Axis-CP": {"name": "Trackster axis - CaloParticle", "lim": deltaAxis_lim, "branch": "EAxis_cp0", "color": ROOT.kBlack}}
histVars = {"DEta": "#Delta#eta", "DPhi": "#Delta#phi"}
eigVal = 'eigVal'
eigVal_max = {"0": 50, "1": 1, "2": 1}
pcaSig = 'pcasig'
pcaSigY = '0'

for E in [10, 100]:
  #outPath = "/eos/user/l/lecriste/HGCal/www"
  #inputPath = "/eos/user/l/lecriste/HGCal/www"
  origin = "/afs/cern.ch/work/l/lecriste/www/HGCAL/"
  inputPath = origin

  inputPath = os.path.join(inputPath,pid_str,pointing)
  outPath = os.path.join(origin,pid_str)
  if not os.path.exists(outPath):
    os.mkdir(outPath)
    os.system('cp '+origin+'index.php '+outPath)

  outPath = os.path.join(outPath,pointing)
  if not os.path.exists(outPath):
    os.mkdir(outPath)

  outPath = os.path.join(outPath, str(E)+"GeV/")
  if not os.path.exists(outPath):
    os.mkdir(outPath)
    os.system('cp '+origin+'index.php '+outPath)

  outPathSingle = os.path.join(outPath,"singleCanvas/")
  if not os.path.exists(outPathSingle):
    os.mkdir(outPathSingle)
    os.system('cp '+origin+'index.php '+outPathSingle)

  rms = {}
  rmsE = {}
  for r in range(25, 160, step):
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

      # Define graphs
      for name in histTitles:
        if name not in rms:
          rms[name] = {}
          rmsE[name] = {}

      # Define histos and graphs
      histCos = ROOT.TH1F("cos_BaryAxis","cos(PCA barycenter, main PCA axis);cos(barycenter, axis)", 100,0.9,1)

      hist = {}
      branchName = {}
      scatter = {}
      for varName, varLabel in histVars.items():
        hist[varName] = {}
        branchName[varName] = {}
        scatter[varName] = ROOT.TH2F("{}".format(varName),"{};{};{}".format(varLabel,histTitles["Bary-CP"]["name"],histTitles["Axis-CP"]["name"]) , binNBary,-scatter_lim,scatter_lim, binNAxis,-scatter_lim,scatter_lim)
        for name, title in histTitles.items():
          hist[varName][name] = ROOT.TH1F("{}_{}".format(name,varName),"{};{}".format(title['name'],varLabel) , 100,-title['lim'],title['lim'])
          branchName[varName][name] = "{}_{}".format(title['branch'], "eta" if "eta" in varLabel else "phi")

          if varName not in rms[name]:
            rms[name][varName] = {}
            rmsE[name][varName] = {}

      histSigmas = {}
      histEigValues = {}
      histPCASigmas = {}
      for i in [0,1,2]:
        histSigmas[sig+str(i)] = ROOT.TH1F("Sigma{}_{}".format(i,format(r, '03')),"#sigma_{} for r={};#sigma_{}".format(i,format(r, '03'),i) , 40,0,10)
        histEigValues[eigVal+str(i)] = ROOT.TH1F("PCA_eigVal{}_{}".format(i,format(r, '03')),"PCA eigenVal_{} for r={};eigenvalue_{}".format(i,format(r, '03'),i) , 50,0,eigVal_max[str(i)])
        histPCASigmas[pcaSig+str(i)] = ROOT.TH1F("PCA_sigma{}_{}".format(i,format(r, '03')),"PCA #sigma_{} for r={};PCA #sigma_{}".format(i,format(r, '03'),i) , 40,0,10)
      histTwoSigmas = ROOT.TH2F("Orig_sigmaYvsX_{}".format(format(r, '03')),"#sigma_y vs #sigma_x for r={};#sigma_x;#sigma_y".format(format(r, '03')), 40,0,10, 40,0,10)
      histTwoPCASigmas = ROOT.TH2F("PCA_sigma1vs{}_{}".format(pcaSigY, format(r, '03')),"PCA #sigma_1 vs #sigma_{} for r={};PCA #sigma_1;PCA #sigma_{}".format(pcaSigY, format(r, '03'), pcaSigY) , 40,0,10, 40,0,10)

      # Loop over tree entries
      for entryNum in range(0, tree.GetEntries()):
        tree.GetEntry(entryNum)

        # Fill histos
        varCos = getattr(tree, "ts_pcaBaryEigVect0_cos")
        histCos.Fill(varCos)

        x, y = 999, 999
        for varName in histVars:
          for name in histTitles:
            var = getattr(tree, branchName[varName][name])
            hist[varName][name].Fill(var)
            if 'barycenter' in histTitles[name]['name']:
              x = var
            else:
              y = var
          scatter[varName].Fill(x,y)

        varSig = getattr(tree, "ts_"+sig)
        varEigVal = getattr(tree, "ts_pcaeigval")
        varPCASig = getattr(tree, "ts_"+pcaSig)
        for i in [0,1,2]:
          histSigmas[sig+str(i)].Fill(varSig[i])
          histEigValues[eigVal+str(i)].Fill(varEigVal[i])
          histPCASigmas[pcaSig+str(i)].Fill(varPCASig[i])
        histTwoSigmas.Fill(varSig[0], varSig[1])
        histTwoPCASigmas.Fill(varPCASig[1], varPCASig[int(pcaSigY)])

      # Plot histos and fill graphs
      canvasCos = ROOT.TCanvas("canvas_cos_r"+format(r, '03'))
      canvasCos.cd()
      ROOT.gStyle.SetOptStat("ourme");
      ROOT.gPad.SetLogy();
      histCos.Draw("h")
      canvasCos.Print(outPathSingle+"cosBaryAxis_r"+format(r, '03')+".png")

      ROOT.gStyle.SetOptStat("rme");
      for varName, varLabel in histVars.items():
        canvas2D = ROOT.TCanvas("canvas_"+varName+format(r, '03'))
        canvas2D.cd()
        scatter[varName].Draw('colz')
        ROOT.gPad.SetGrid()
        canvas2D.Print(outPathSingle+"Scatter"+varName+"_r"+format(r, '03')+".png")

        canvasMulti = ROOT.TCanvas("canvasMulti_"+varName+format(r, '03'))
        canvasMulti.Divide(2,2)
        for name, title in histTitles.items():
          rms[name][varName][format(r, '03')] = hist[varName][name].GetRMS()
          rmsE[name][varName][format(r, '03')] = hist[varName][name].GetRMSError()

          canvas = ROOT.TCanvas("canvas_"+branchName[varName][name]+format(r, '03'))
          canvas.cd()
          hist[varName][name].Draw("h")
          canvas.Print(outPathSingle+branchName[varName][name]+"_r"+format(r, '03')+".png")

          if 'barycenter' in histTitles[name]['name']:
            canvasMulti.cd(1)
          else:
            canvasMulti.cd(3)
          hist[varName][name].Draw("h")
        canvasMulti.cd(2)
        scatter[varName].Draw('colz')
        canvasMulti.cd(4)
        histCos.Draw("h")
        canvasMulti.Print(outPath+varName+"_r"+format(r, '03')+".png")

      for i in [0,1,2]:
        canvasSig = ROOT.TCanvas("canvas_sig"+str(i)+"_r"+format(r, '03'))
        canvasSig.cd()
        histSigmas[sig+str(i)].Draw("h")
        canvasSig.Print(outPathSingle+sig+str(i)+"_r"+format(r, '03')+".png")

        canvasEigVal = ROOT.TCanvas("canvas_eigVal"+str(i)+"_r"+format(r, '03'))
        canvasEigVal.cd()
        histEigValues[eigVal+str(i)].Draw("h")
        canvasEigVal.Print(outPathSingle+eigVal+str(i)+"_r"+format(r, '03')+".png")

        canvasPCASig = ROOT.TCanvas("canvas_PCASig"+str(i)+"_r"+format(r, '03'))
        canvasPCASig.cd()
        histPCASigmas[pcaSig+str(i)].Draw("h")
        canvasPCASig.Print(outPathSingle+pcaSig+str(i)+"_r"+format(r, '03')+".png")

      canvasTwoSig = ROOT.TCanvas("canvas_sigYvsX_r"+format(r, '03'))
      canvasTwoSig.cd()
      histTwoSigmas.Draw("colz")
      canvasTwoSig.Print(outPath+"SigYvsSigX_r"+format(r, '03')+".png")

      canvasTwoPCASig = ROOT.TCanvas("canvas_PCASig1vs+"+pcaSigY+"+_r"+format(r, '03'))
      canvasTwoPCASig.cd()
      histTwoPCASigmas.Draw("colz")
      canvasTwoPCASig.Print(outPath+"pcaSig1vs"+pcaSigY+"_r"+format(r, '03')+".png")

      inFile.Close()

      from array import array
      for varName in histVars:
        canvas = ROOT.TCanvas("canvas_"+varName)
        gr = {}
        for name in histTitles:
          n = len(rms[name][varName])
          x, y, xE, yE = array('d'), array('d'), array('d'), array('d')
          for point in sorted(rms[name][varName]):
            x.append(int(point));
            xE.append(0);
            y.append(rms[name][varName][point])
            yE.append(rmsE[name][varName][point])
          gr[name] = ROOT.TGraphErrors(n, x, y, xE, yE)
          gr[name].SetTitle( name );
          gr[name].GetXaxis().SetTitle( "r" )
          gr[name].GetYaxis().SetTitle( "RMS("+histVars[varName]+")" )
          #gr[name].SetMarkerColor( histTitles[name]['color'] )
          gr[name].SetLineColor( histTitles[name]['color'] )
          gr[name].GetHistogram().SetMaximum(3*(10**-1))
          gr[name].GetHistogram().SetMinimum(10**-4)
          same = 'A' if len(gr) < 2 else "SAME "
          gr[name].Draw( same+'CP' )
          ROOT.gPad.SetLogy();
          ROOT.gPad.SetGrid();
        ROOT.gPad.BuildLegend();
        canvas.Print(outPath+varName+"_RMS.png")
