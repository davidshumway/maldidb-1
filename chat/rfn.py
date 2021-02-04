from rpy2.robjects import r as R
import rpy2.robjects as robjects
import json

'''
todo:
-- If the list passed to MQ:binPeaks is too large, RAM use becomes
  too high / exhausted. In this case, we can work around by breaking
  the list into smaller manageable lists and performing binPeaks
  on these smaller lists. On each round of binPeaks, remove the low-
  scoring matches. If, on the next round, the list is still too large,
  do another round of smaller list binning. Realistically, this should
  never go past a few rounds.
-- allPeaks, allSpectra, and binnedPeaks all are, e.g., list=(...), len=24424
-- show a plot of memory size and number of spectra being compared
'''

# collapse
R('''
  collapseReplicates <- function(checkedPool,
                                 sampleIDs,
                                 peakPercentPresence,
                                 lowerMassCutoff,
                                 upperMassCutoff, 
                                 minSNR, 
                                 tolerance = 0.002,
                                 protein){
    
    validate(need(is.numeric(peakPercentPresence), "peakPercentPresence not numeric"))
    validate(need(is.numeric(lowerMassCutoff), "lowerMassCutoff not numeric"))
    validate(need(is.numeric(upperMassCutoff), "upperMassCutoff not numeric"))
    validate(need(is.numeric(minSNR), "minSNR not numeric"))
    validate(need(is.numeric(tolerance), "tolerance not numeric"))
    validate(need(is.logical(protein), "protein not logical"))
    
    temp <- IDBacApp::getPeakData(checkedPool = checkedPool,
                                  sampleIDs = sampleIDs,
                                  protein = protein) 
    req(length(temp) > 0)
    # Binning peaks lists belonging to a single sample so we can filter 
    # peaks outside the given threshold of presence 
    
    for (i in 1:length(temp)) {
      snr1 <-  which(MALDIquant::snr(temp[[i]]) >= minSNR)
      temp[[i]]@mass <- temp[[i]]@mass[snr1]
      temp[[i]]@snr <- temp[[i]]@snr[snr1]
      temp[[i]]@intensity <- temp[[i]]@intensity[snr1]
    }
    
    specNotZero <- sapply(temp, function(x) length(x@mass) > 0)
    
    # Only binPeaks if spectra(um) has peaks.
    # see: https://github.com/sgibb/MALDIquant/issues/61 for more info 
    # note: MALDIquant::binPeaks does work if there is only one spectrum
    if (any(specNotZero)) {
      
      temp <- temp[specNotZero]
      temp <- MALDIquant::binPeaks(temp,
                                   tolerance = tolerance, 
                                   method = c("strict")) 
      
      temp <- MALDIquant::filterPeaks(temp,
                                      minFrequency = peakPercentPresence / 100) 
      
      temp <- MALDIquant::mergeMassPeaks(temp, 
                                         method = "mean") 
      temp <- MALDIquant::trim(temp,
                               c(lowerMassCutoff,
                                 upperMassCutoff))
    } else {
      temp <- MALDIquant::mergeMassPeaks(temp, 
                                         method = "mean") 
    }
    
    return(temp)
  }
  ''')

R('''
createMassSpectrum <- function(mass, intensity) {
  MALDIquant::createMassSpectrum(mass, intensity)
}
createMassPeaks <- function(mass, intensity, snr) {
  MALDIquant::createMassPeaks(
    mass = mass, intensity = intensity, snr = as.numeric(snr)
  )
}
''')

class SpectraScores():
  '''
  from rpy2.robjects import r as R
  import rpy2.robjects as robjects
  '''
  
  def __init__(self):
    self.all_peaks = []
    self.all_spectra = []
  
  def bin_peaks(self):
    return R['binPeaks'](self.all_peaks, self.all_spectra)
    
  def append_spectra(self, mass, intensity, snr):
    m = robjects.FloatVector(json.loads('[' + mass + ']'))
    i = robjects.FloatVector(json.loads('[' + intensity + ']'))
    s = robjects.FloatVector(json.loads('[' + snr + ']'))
    self.all_peaks.append(
      R['createMassPeaks'](m, i, s)
    )
    self.all_spectra.append(
      R['createMassSpectrum'](m, i)
    )
    
# bin
R('''
  suppressPackageStartupMessages(library(IDBacApp))
  # Some globals
  #allSpectra <- list()
  #allPeaks <- list()
  #binnedPeaks <- F
  #resetGlobal <- function() {
  #  allSpectra <<- list()
  #  allPeaks <<- list()
  #  binnedPeaks <<- F
  # ~ #}
  # ~ appendSpectra <- function(m, i, s) {
    # ~ # <<-: assign upward
    # ~ # allPeaks: Used for binPeaks, intensityMatrix
    # ~ # allSpectra: Used for intensityMatrix
    # ~ # todo: createMassPeaks -- snr = as.numeric(x$snr))
    # ~ allSpectra <<- append(
      # ~ allSpectra,
      # ~ MALDIquant::createMassSpectrum(mass = m, intensity = i)
    # ~ )
    # ~ allPeaks <<- append(
      # ~ allPeaks,
      # ~ MALDIquant::createMassPeaks(
        # ~ mass = m, intensity = i, snr = as.numeric(s)
      # ~ )
    # ~ )
  # ~ }
  showMem <- function() {
    print('x')
    for (itm in ls()) { 
      print(formatC(c(itm, object.size(get(itm))), 
          format="d", 
          big.mark=",", 
          width=30), 
          quote=F)
    }
  }
  binPeaks <- function(allPeaks, allSpectra) {
    #print(class(allPeaks)) # list
    #print(class(allSpectra))
    print("length(allPeaks)")
    print(length(allPeaks))
    print("length(allSpectra)")
    print(length(allSpectra))
    showMem()
    # Only scores in first row are relevant, i.e., input spectra
    # Finally, order the row by score decreasing
    binnedPeaks <- MALDIquant::binPeaks(allPeaks, tolerance = 0.002)
    print("length(binnedPeaks)")
    print(length(binnedPeaks))
    print(is(binnedPeaks))
    print(object.size(allSpectra))
    print(object.size(allPeaks))
    print(object.size(binnedPeaks))
    # ram issue here:
    featureMatrix <- MALDIquant::intensityMatrix(binnedPeaks, allSpectra)
    print("dim(featureMatrix)")
    print(dim(featureMatrix))
    print(is(binnedPeaks))
    print(object.size(featureMatrix))
    showMem()
    
    d <- stats::as.dist(coop::tcosine(featureMatrix))
    d <- as.matrix(d)
    d <- round(d, 3)
    
    # Reorder later
    #d <- d[,order(d[,1],decreasing = T)]
    
    # Discard symmetric part of matrix
    d[lower.tri(d, diag = FALSE)] <- NA
    
    # ~ print(d[1,][0])
    print(d[2,])
    
    d <- d[1,] # first row
  }
  
  # heatmap code
  binSpectraOLD <- function() {
    binnedPeaks <- MALDIquant::binPeaks(allPeaks, tolerance = 0.002)
    featureMatrix <- MALDIquant::intensityMatrix(binnedPeaks, allSpectra)
    
    
    # Utilizing: github.com/strejcem/MALDIvs16S/blob/master/R/MALDIbacteria.R
    # ~ similarity <- coop::cosine(t(featureMatrix))
    # ~ d <- as.dist(1-similarity) ### ???
    # ~ d <- as.dist(similarity)
    
    # IDBac: stats::as.dist(1 - coop::tcosine(data))
    # ~ d <- stats::as.dist(1 - coop::tcosine(featureMatrix))
    d <- stats::as.dist(coop::tcosine(featureMatrix))
    
    x <- as.matrix(d)
    x <- round(x, 2)
    #print('d')
    #print(d)
    
    #jpeg(file = "test.jpg", quality = 100, width = 2000, height = 2000)
    png(file = "test.png", width = 3000, height = 3000, res = 300, pointsize = 6)
    # ~ heatmap(d) #, col = palette, symm = TRUE)
    # ~ heatmap(as.matrix(d[, -1])) #, col = palette, symm = TRUE)
    heatmap(x, symm = FALSE, Colv = NA, Rowv = NA) #, col = palette, symm = TRUE)
    # ~ heatmap.2(as.matrix(d), symm = FALSE) #, col = palette, symm = TRUE)
    dev.off()
    
    # small section
    png(file = "test-sm.png", width = 1000, height = 1000, res = 300, pointsize = 6)
    heatmap(x[1:16,1:16], symm = FALSE, Colv = NA, Rowv = NA) #, col = palette, symm = TRUE)
    dev.off()
    
    library(gplots)
    png(file = "test2-sm.png", width = 1200, height = 1200, res = 300, pointsize = 6)
    gplots::heatmap.2(x[1:16,1:16], symm = FALSE, Colv = NA, Rowv = NA, cellnote = x[1:16,1:16], notecex = 0.5, trace = "none")
    dev.off()
    
    png(file = "test2-med.png", width = 1200, height = 1200, res = 300, pointsize = 6)
    gplots::heatmap.2(x[1:32,1:32], symm = FALSE, Colv = NA, Rowv = NA, cellnote = x[1:32,1:32], notecex = 0.5, trace = "none")
    dev.off()
    
    png(file = "test3-sm.png", width = 1200, height = 1200, res = 300, pointsize = 6)
    y <- x
    y[lower.tri(x, diag = FALSE)] <- NA
    gplots::heatmap.2(y[1:16,1:16], symm = FALSE, Colv = NA, Rowv = NA, cellnote = y[1:16,1:16], notecex = 0.5, trace = "none")
    dev.off()
    
    png(file = "test3-med.png", width = 1200, height = 1200, res = 300, pointsize = 6)
    y <- x
    y[lower.tri(x, diag = FALSE)] <- NA
    gplots::heatmap.2(y[1:32,1:32], symm = FALSE, Colv = NA, Rowv = NA, cellnote = y[1:32,1:32], notecex = 0.5, trace = "none")
    dev.off()
    
    png(file = "test3-full.png", width = 3000, height = 3000, res = 300, pointsize = 6)
    y <- x
    y[lower.tri(x, diag = FALSE)] <- NA
    gplots::heatmap.2(y, symm = FALSE, Colv = NA, Rowv = NA, trace = "none")
    dev.off()
    
    
    png(file = "test4-sm.png", width = 1200, height = 1200, res = 300, pointsize = 6)
    y <- x
    y[y == 0] <- 1
    gplots::heatmap.2(y[1:16,1:16], symm = FALSE, cellnote = y[1:16,1:16], notecex = 0.5, trace = "none")
    dev.off()
    
    png(file = "test4-med.png", width = 1200, height = 1200, res = 300, pointsize = 6)
    y <- x
    y[y == 0] <- 1
    gplots::heatmap.2(y[1:32,1:32], symm = FALSE, cellnote = y[1:32,1:32], notecex = 0.5, trace = "none")
    dev.off()
    
    png(file = "test4-full.png", width = 3000, height = 3000, res = 300, pointsize = 6)
    y <- x
    y[y == 0] <- 1
    gplots::heatmap.2(y, symm = FALSE, trace = "none")
    dev.off()
    
  }
''')
