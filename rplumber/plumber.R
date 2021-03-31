#* Example query:
#* $ curl -H "Content-Type: application/json" --data '{"ids":[1,2,3]}'
#*   http://localhost:8000/sum

suppressPackageStartupMessages(library(IDBacApp))
require('RPostgreSQL')

#* Echo
#*
#* @get /test
function() {
  return(
    list(name = 'Test')
  )
}

#* Return driver and connection
connect <- function() {
  # env variables
  POSTGRES_USER <- Sys.getenv('POSTGRES_USER')
  POSTGRES_PASSWORD <- Sys.getenv('POSTGRES_PASSWORD')
  POSTGRES_DB <- Sys.getenv('POSTGRES_DB')
  DATABASE_HOST <- Sys.getenv('DATABASE_HOST')
  DATABASE_PORT <- Sys.getenv('DATABASE_PORT')
  drv <- dbDriver('PostgreSQL')
  con <- dbConnect(
    drv, dbname = POSTGRES_DB,
    host = DATABASE_HOST, port = DATABASE_PORT,
    user = POSTGRES_USER, password = POSTGRES_PASSWORD
  )
  list('drv' = drv, 'con' = con)
}
disconnect <- function(driver, connection) {
  dbDisconnect(connection)
  dbUnloadDriver(driver)
}

# auxiliary print function
print.data.frame <- function (
  x, ..., maxchar=20, digits = NULL, quote = FALSE, right = TRUE,
  row.names = TRUE) 
{
  x <- as.data.frame(
    lapply(x, function(xx) {
      if (is.character(xx))
        paste0(substr(xx, 1, maxchar), '...')
      else if (is.list(xx))
        xx
      else xx
    })
  )
  base::print.data.frame(
    x, ..., digits=digits, quote=quote, right=right, 
    row.names=row.names
  )
}

#* Bin peaks: Get cosine scores for an unknown vs. set of db spectra
#*  -- ids must correlate to at least 1 row
#*     furthermore, stop if ids does not match db results??
#*  -- id refers to spectra in question, from SearchSpectra table
#* @param req Built-in
#* @param id List of IDs from SearchSpectra table
#* @param ids List of IDs from Spectra table
#* @post /binPeaks
function(req, id, ids) {
  if (class(ids) != 'integer') {
    stop('not an integer (ids)!') # stop throws 500
  }
  if (class(id) != 'integer') {
    stop('not an integer (id)!')
  }
  if (length(ids) < 1) {
    stop('less than one comparison id given!')
  }
  
  c <- connect()
  s <- paste(unlist(ids), collapse = ',')
  s <- paste0('SELECT peak_mass, peak_intensity, peak_snr
    FROM chat_spectra
    WHERE id IN (', s, ')')
  q <- dbGetQuery(c$con, s)
  if (nrow(q) < 1) {
    disconnect(c$drv, c$con)
    stop('database returned less than one row (spectra)!')
  }
  s <- paste0('SELECT peak_mass, peak_intensity, peak_snr
    FROM chat_searchspectra
    WHERE id = "', id, '"')
  q2 <- dbGetQuery(c$con, s)
  if (nrow(q2) != 1) {
    disconnect(c$drv, c$con)
    stop('database did not return exactly one row (searchspectra)!')
  }
  
  allSpectra = list()
  allPeaks = list()
  
  for(i in 1:nrow(q2)) { # unknown spectra
    row <- q2[i,]
    allPeaks <- append(allPeaks,
      MALDIquant::createMassPeaks(
        mass = as.numeric(strsplit(row$peak_mass, ",")[[1]]),
        intensity = as.numeric(strsplit(row$peak_intensity, ",")[[1]]),
        snr = as.numeric(strsplit(row$peak_snr, ",")[[1]]))
    )
    allSpectra <- append(allSpectra,
      MALDIquant::createMassSpectrum(
        mass = as.numeric(strsplit(row$peak_mass, ",")[[1]]),
        intensity = as.numeric(strsplit(row$peak_intensity, ",")[[1]]))
    )
  }
  for(i in 1:nrow(q)) {
    row <- q[i,]
    allPeaks <- append(allPeaks,
      MALDIquant::createMassPeaks(
        mass = as.numeric(strsplit(row$peak_mass, ",")[[1]]),
        intensity = as.numeric(strsplit(row$peak_intensity, ",")[[1]]),
        snr = as.numeric(strsplit(row$peak_snr, ",")[[1]]))
    )
    allSpectra <- append(allSpectra,
      MALDIquant::createMassSpectrum(
        mass = as.numeric(strsplit(row$peak_mass, ",")[[1]]),
        intensity = as.numeric(strsplit(row$peak_intensity, ",")[[1]]))
    )
  }
  
#~   print('len')
#~   print(length(allPeaks))
#~   print('dim')
#~   print(dim(allPeaks))
  
  binnedPeaks <- MALDIquant::binPeaks(allPeaks, tolerance = 0.002)
  featureMatrix <- MALDIquant::intensityMatrix(binnedPeaks, allSpectra)

  d <- stats::as.dist(coop::tcosine(featureMatrix))
  d <- as.matrix(d)
  d <- round(d, 3)
  d[lower.tri(d, diag = FALSE)] <- NA # Discard symmetric part of matrix
  d <- d[1,] # return just first row
  
  disconnect(c$drv, c$con)
  d
}

#* Cosine: Get cosine scores for a set of db spectra
#* -- ids must correlate to at least 2 rows
#* @param req Built-in
#* @param ids List of IDs from Spectra table
#* @post /cosine
function(req, ids) {
  print('got ids')
  print(ids)
  print(class(ids)) # character
#~   if (class(ids) != 'integer') {
#~     stop('not an integer (ids)!')
#~   }
  if (length(ids) < 2) {
    stop('less than two comparison ids given!')
  }
  
  c <- connect()
  s <- paste(unlist(ids), collapse = ',')
  s <- paste0('SELECT peak_mass, peak_intensity, peak_snr
    FROM chat_spectra
    WHERE id IN (', s, ')')
  q <- dbGetQuery(c$con, s)
  if (nrow(q) < 2) {
    disconnect(c$drv, c$con)
    stop('database returned less than two spectra!')
  }
  
  allSpectra = list()
  allPeaks = list()
  
  for(i in 1:nrow(q)) {
    row <- q[i,]
    allPeaks <- append(allPeaks,
      MALDIquant::createMassPeaks(
        mass = as.numeric(strsplit(row$peak_mass, ",")[[1]]),
        intensity = as.numeric(strsplit(row$peak_intensity, ",")[[1]]),
        snr = as.numeric(strsplit(row$peak_snr, ",")[[1]]))
    )
    allSpectra <- append(allSpectra,
      MALDIquant::createMassSpectrum(
        mass = as.numeric(strsplit(row$peak_mass, ",")[[1]]),
        intensity = as.numeric(strsplit(row$peak_intensity, ",")[[1]]))
    )
  }
  
  binnedPeaks <- MALDIquant::binPeaks(allPeaks, tolerance = 0.002)
  featureMatrix <- MALDIquant::intensityMatrix(binnedPeaks, allSpectra)
  
  d <- stats::as.dist(coop::tcosine(featureMatrix))
  d <- as.matrix(d)
  d <- round(d, 3)
  dfull <- d
  d[lower.tri(d, diag = FALSE)] <- NA # Discard symmetric part
  disconnect(c$drv, c$con)
  
  library(jsonlite)
  a <- list( # capture output helpful for serializing S4 class
    'ids' = ids,
    'allPeaks' = capture.output(allPeaks),
    'allSpectra' = capture.output(allSpectra),
    'binnedPeaks' = capture.output(binnedPeaks),
    'featureMatrix' = capture.output(featureMatrix),
    'cosineScores' = capture.output(dfull),
    'cosineScoresUt' = capture.output(d)
  )
  jsonlite::toJSON(a)
}

#* Preprocess: Preprocess spectra files
#* @param file File path to preprocess
#* @get /preprocess
preprocess <- function(file) {
  smallRangeEnd <- 6000
  
  print(getwd())
  print(file)
  f <- file.path(paste0("/app/", file))
  
#~   f <- file.path(getwd(), paste0('media/', f))
  mzML_con <- mzR::openMSfile(f, backend = "pwiz")
  scanNumber <- nrow(mzR::header(mzML_con))
  print('scanNumber')
  print(scanNumber)
  
  spectraImport <- mzR::peaks(mzML_con) # matrix
  print('spectraImport1')
  print(class(spectraImport))
  #print(spectraImport)
  
  spectraImport <- IDBacApp::spectrumMatrixToMALDIqaunt(spectraImport) # mass spectrum
  print('spectraImport2')
  print(class(spectraImport))
  #print(spectraImport)
  
  # logical vector of maximum masses of mass vectors.
  # True = small mol, False = protein
  smallIndex <- unlist(lapply(spectraImport, function(x) max(x@mass)))
  smallIndex <- smallIndex < smallRangeEnd
  envSm <- FALSE
  envPr <- FALSE
  if (any(smallIndex)) {
   envSm <- IDBacApp::processXMLIndSpectra(
     spectraImport = spectraImport,
     smallOrProtein = "small",
     index = smallIndex)
  }
  if (any(!smallIndex)) {
   envPr <- IDBacApp::processXMLIndSpectra(
     spectraImport = spectraImport,
     smallOrProtein = "protein",
     index = !smallIndex)
    x <- collapseReplicates(
      IDBacApp::processProteinSpectra(spectraImport[!smallIndex])
    )
  }
  print('env')
  print(envSm)
  print(envPr)
  print(x)
  
#~   if (scanNumber != 1) { # collapse replicates ~~
   #return(list('error' = paste('scan number is not one:', scanNumber)))
#~    x <- collapseReplicates(envPr$peakMatrix)
#~   }
  
#~   return(list('env_sm' = envSm, 'env_pr' = envPr))
  return(list('x' = x))
}

collapseReplicates <- function(temp) {
#~     checkedPool,
#~     sampleIDs,
#~     peakPercentPresence,
#~     lowerMassCutoff,
#~     upperMassCutoff, 
#~     minSNR, 
#~     tolerance = 0.002,
#~     protein

#~   validate(need(is.numeric(peakPercentPresence), "peakPercentPresence not numeric"))
#~   validate(need(is.numeric(lowerMassCutoff), "lowerMassCutoff not numeric"))
#~   validate(need(is.numeric(upperMassCutoff), "upperMassCutoff not numeric"))
#~   validate(need(is.numeric(minSNR), "minSNR not numeric"))
#~   validate(need(is.numeric(tolerance), "tolerance not numeric"))
#~   validate(need(is.logical(protein), "protein not logical"))

  #temp <- IDBacApp::getPeakData(checkedPool = checkedPool,
  #                              sampleIDs = sampleIDs,
  #                              protein = protein) 
  # getPeakData::
#~   temp <- lapply(temp,
#~    function(x){
#~      MALDIquant::createMassPeaks(
#~        mass = x$mass,
#~        intensity = x$intensity ,
#~        snr = as.numeric(x$snr))
#~    }
#~   )
  minSNR <- 3 # min SNR is 3 for protein data
  tolerance <- 0.002
  peakPercentPresence <- 70
  lowerMassCutoff <- 2000
  upperMassCutoff <- 20000
  
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
  temp
}

# --------------------
# From rfn.py / Rpy2
# --------------------



# ~ R('''
# ~ createMassSpectrum__ <- function(mass, intensity) {
  # ~ MALDIquant::createMassSpectrum(mass, intensity)
# ~ }
# ~ createMassPeaks__ <- function(mass, intensity, snr) {
  # ~ MALDIquant::createMassPeaks(
    # ~ mass = mass, intensity = intensity, snr = as.numeric(snr)
  # ~ )
# ~ }
# ~ ''')

# ~ # bin
# ~ R('''
  # ~ showMem <- function() {
    # ~ print('x')
    # ~ for (itm in ls()) { 
      # ~ print(formatC(c(itm, object.size(get(itm))), 
          # ~ format="d", 
          # ~ big.mark=",", 
          # ~ width=30), 
          # ~ quote=F)
    # ~ }
  # ~ }
  # ~ binPeaks <- function(allPeaks, allSpectra) {
    # ~ showMem()
    # ~ # Only scores in first row are relevant, i.e., input spectra
    # ~ # Finally, order the row by score decreasing
    # ~ binnedPeaks <- MALDIquant::binPeaks(allPeaks, tolerance = 0.002)
    # ~ # ram issue here:
    # ~ featureMatrix <- MALDIquant::intensityMatrix(binnedPeaks, allSpectra)
    # ~ showMem()
    
    # ~ d <- stats::as.dist(coop::tcosine(featureMatrix))
    # ~ d <- as.matrix(d)
    # ~ d <- round(d, 3)
    
    # ~ # Reorder later
    # ~ #d <- d[,order(d[,1],decreasing = T)]
    
    # ~ # Discard symmetric part of matrix
    # ~ d[lower.tri(d, diag = FALSE)] <- NA
    # ~ print(d[2,])
    
    # ~ d <- d[1,] # first row
  # ~ }
  # ~ binPeaksInfo <- function(allPeaks, allSpectra) {
    # ~ #library(jsonlite)
    # ~ # bp: a list of MassPeaks objects
    # ~ binnedPeaks <- MALDIquant::binPeaks(allPeaks, tolerance = 0.002)
    # ~ featureMatrix <- MALDIquant::intensityMatrix(binnedPeaks, allSpectra)
    # ~ d <- stats::as.dist(coop::tcosine(featureMatrix))
    # ~ d <- as.matrix(d)
    # ~ d <- round(d, 3)
    # ~ ut <- d
    # ~ ut[lower.tri(ut, diag = FALSE)] <- NA
    # ~ n <- list(
      # ~ "binnedPeaks" = binnedPeaks,
      # ~ "featureMatrix" = featureMatrix,
      # ~ "cosineScores" = d,
      # ~ "cosineScoresUt" = ut
    # ~ )
    # ~ #toJSON(n, pretty = FALSE)
    # ~ #return()
  # ~ }
  
  # ~ # heatmap code
  # ~ binSpectraOLD <- function() {
    # ~ binnedPeaks <- MALDIquant::binPeaks(allPeaks, tolerance = 0.002)
    # ~ featureMatrix <- MALDIquant::intensityMatrix(binnedPeaks, allSpectra)
    
    
    # ~ # Utilizing: github.com/strejcem/MALDIvs16S/blob/master/R/MALDIbacteria.R
    
    # ~ # IDBac: stats::as.dist(1 - coop::tcosine(data))
    # ~ d <- stats::as.dist(coop::tcosine(featureMatrix))
    
    # ~ x <- as.matrix(d)
    # ~ x <- round(x, 2)
    # ~ #print('d')
    # ~ #print(d)
    
    # ~ #jpeg(file = "test.jpg", quality = 100, width = 2000, height = 2000)
    # ~ png(file = "test.png", width = 3000, height = 3000, res = 300, pointsize = 6)
    # ~ heatmap(x, symm = FALSE, Colv = NA, Rowv = NA) #, col = palette, symm = TRUE)
    # ~ dev.off()
    
    # ~ # small section
    # ~ png(file = "test-sm.png", width = 1000, height = 1000, res = 300, pointsize = 6)
    # ~ heatmap(x[1:16,1:16], symm = FALSE, Colv = NA, Rowv = NA) #, col = palette, symm = TRUE)
    # ~ dev.off()
    
    # ~ library(gplots)
    # ~ png(file = "test2-sm.png", width = 1200, height = 1200, res = 300, pointsize = 6)
    # ~ gplots::heatmap.2(x[1:16,1:16], symm = FALSE, Colv = NA, Rowv = NA, cellnote = x[1:16,1:16], notecex = 0.5, trace = "none")
    # ~ dev.off()
    
    # ~ png(file = "test2-med.png", width = 1200, height = 1200, res = 300, pointsize = 6)
    # ~ gplots::heatmap.2(x[1:32,1:32], symm = FALSE, Colv = NA, Rowv = NA, cellnote = x[1:32,1:32], notecex = 0.5, trace = "none")
    # ~ dev.off()
    
    # ~ png(file = "test3-sm.png", width = 1200, height = 1200, res = 300, pointsize = 6)
    # ~ y <- x
    # ~ y[lower.tri(x, diag = FALSE)] <- NA
    # ~ gplots::heatmap.2(y[1:16,1:16], symm = FALSE, Colv = NA, Rowv = NA, cellnote = y[1:16,1:16], notecex = 0.5, trace = "none")
    # ~ dev.off()
    
    # ~ png(file = "test3-med.png", width = 1200, height = 1200, res = 300, pointsize = 6)
    # ~ y <- x
    # ~ y[lower.tri(x, diag = FALSE)] <- NA
    # ~ gplots::heatmap.2(y[1:32,1:32], symm = FALSE, Colv = NA, Rowv = NA, cellnote = y[1:32,1:32], notecex = 0.5, trace = "none")
    # ~ dev.off()
    
    # ~ png(file = "test3-full.png", width = 3000, height = 3000, res = 300, pointsize = 6)
    # ~ y <- x
    # ~ y[lower.tri(x, diag = FALSE)] <- NA
    # ~ gplots::heatmap.2(y, symm = FALSE, Colv = NA, Rowv = NA, trace = "none")
    # ~ dev.off()
    
    
    # ~ png(file = "test4-sm.png", width = 1200, height = 1200, res = 300, pointsize = 6)
    # ~ y <- x
    # ~ y[y == 0] <- 1
    # ~ gplots::heatmap.2(y[1:16,1:16], symm = FALSE, cellnote = y[1:16,1:16], notecex = 0.5, trace = "none")
    # ~ dev.off()
    
    # ~ png(file = "test4-med.png", width = 1200, height = 1200, res = 300, pointsize = 6)
    # ~ y <- x
    # ~ y[y == 0] <- 1
    # ~ gplots::heatmap.2(y[1:32,1:32], symm = FALSE, cellnote = y[1:32,1:32], notecex = 0.5, trace = "none")
    # ~ dev.off()
    
    # ~ png(file = "test4-full.png", width = 3000, height = 3000, res = 300, pointsize = 6)
    # ~ y <- x
    # ~ y[y == 0] <- 1
    # ~ gplots::heatmap.2(y, symm = FALSE, trace = "none")
    # ~ dev.off()
    
  # ~ }
# ~ ''')
